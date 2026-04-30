import boto3, json, os, zipfile, time

REGION  = "us-east-1"
PROJECT = "aws-api-project"

LAMBDAS = {
    "data-handler":    "../lambdas/data_handler/lambda_function.py",
    "image-processor": "../lambdas/image_processor/lambda_function.py",
    "user-manager":    "../lambdas/user_manager/lambda_function.py",
}
STAGES = ["dev", "test", "prod"]

lambda_client = boto3.client("lambda",     region_name=REGION)
apigw_client  = boto3.client("apigateway", region_name=REGION)

def get_role_arn():
   
    account_id = boto3.client("sts").get_caller_identity()["Account"]
    
   
    role_arn = f"arn:aws:iam::{account_id}:role/LambdaExecutionRole"
    
    print(f"   Role detected for account {account_id}: {role_arn}")
    return role_arn

def zip_lambda(py_file, zip_path):
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(py_file, "lambda_function.py")
    print(f"  ✅ Zipped: {zip_path}")

def deploy_lambda(name, py_file, role_arn):
    full_name = f"{PROJECT}-{name}"
    zip_path  = f"/tmp/{name}.zip"
    zip_lambda(py_file, zip_path)
    with open(zip_path, "rb") as f:
        code = f.read()

    try:
        lambda_client.create_function(
            FunctionName=full_name,
            Runtime="python3.10",
            Role=role_arn,
            Handler="lambda_function.lambda_handler",
            Code={"ZipFile": code},
            Timeout=30,
            MemorySize=128,
            Description=f"{name} - {PROJECT}",
        )
        print(f"  🆕 Created: {full_name}")
        time.sleep(8)
    except lambda_client.exceptions.ResourceConflictException:
        lambda_client.update_function_code(FunctionName=full_name, ZipFile=code)
        print(f"  🔄 Updated: {full_name}")
        time.sleep(3)

    arn = lambda_client.get_function_configuration(FunctionName=full_name)["FunctionArn"]
    return arn

def create_api(lambda_arns):
    api_name = f"{PROJECT}-api"
    apis     = apigw_client.get_rest_apis().get("items", [])
    existing = next((a for a in apis if a["name"] == api_name), None)

    if existing:
        api_id = existing["id"]
        print(f"  ♻️  Existing API: {api_id}")
    else:
        api    = apigw_client.create_rest_api(
            name=api_name,
            description="Multi-stage API Gateway",
            endpointConfiguration={"types": ["REGIONAL"]},
        )
        api_id = api["id"]
        print(f"  🆕 Created API: {api_id}")

    root_id = apigw_client.get_resources(restApiId=api_id)["items"][0]["id"]
    routes  = {
        "data":   lambda_arns["data-handler"],
        "images": lambda_arns["image-processor"],
        "users":  lambda_arns["user-manager"],
    }
    for path, fn_arn in routes.items():
        _setup_resource(api_id, root_id, path, fn_arn)
    return api_id

def _setup_resource(api_id, root_id, path, fn_arn):
    resources   = apigw_client.get_resources(restApiId=api_id)["items"]
    existing    = next((r for r in resources if r.get("pathPart") == path), None)
    if existing:
        resource_id = existing["id"]
        print(f"  ♻️  Resource /{path} exists")
    else:
        resource_id = apigw_client.create_resource(
            restApiId=api_id, parentId=root_id, pathPart=path)["id"]
        print(f"  ✅ Resource /{path} created")

    account_id = boto3.client("sts").get_caller_identity()["Account"]
    uri = f"arn:aws:apigateway:{REGION}:lambda:path/2015-03-31/functions/{fn_arn}/invocations"

    for method in ["GET", "POST", "PUT", "DELETE"]:
        try:
            apigw_client.get_method(restApiId=api_id, resourceId=resource_id, httpMethod=method)
            print(f"     ♻️  {method} /{path} exists")
        except apigw_client.exceptions.NotFoundException:
            apigw_client.put_method(restApiId=api_id, resourceId=resource_id,
                httpMethod=method, authorizationType="NONE")
            apigw_client.put_integration(restApiId=api_id, resourceId=resource_id,
                httpMethod=method, type="AWS_PROXY", integrationHttpMethod="POST", uri=uri)
            print(f"     ✅ {method} /{path}")

    fn_name = fn_arn.split(":")[-1]
    try:
        lambda_client.add_permission(
            FunctionName=fn_name,
            StatementId=f"apigw-{path}-{api_id}",
            Action="lambda:InvokeFunction",
            Principal="apigateway.amazonaws.com",
            SourceArn=f"arn:aws:execute-api:{REGION}:{account_id}:{api_id}/*/*/{path}",
        )
        print(f"  🔐 Permission added: /{path}")
    except lambda_client.exceptions.ResourceConflictException:
        pass

def deploy_stages(api_id):
    endpoints = {}
    for stage in STAGES:
        try:
            apigw_client.get_stage(restApiId=api_id, stageName=stage)
            print(f"  ♻️  Stage '{stage}' exists")
        except apigw_client.exceptions.NotFoundException:
            apigw_client.create_deployment(restApiId=api_id, stageName=stage)
            print(f"  🆕 Stage '{stage}' deployed")

        if stage == "prod":
            try:
                apigw_client.update_stage(restApiId=api_id, stageName=stage,
                    patchOperations=[
                        {"op": "replace", "path": "/cacheClusterEnabled", "value": "true"},
                        {"op": "replace", "path": "/cacheClusterSize",    "value": "0.5"},
                    ])
                print(f"  ✅ Cache enabled on prod")
            except Exception as e:
                print(f"  ⚠️  Cache skipped: {e}")

        endpoints[stage] = f"https://{api_id}.execute-api.{REGION}.amazonaws.com/{stage}"
    return endpoints

def save_config(api_id, lambda_arns, endpoints):
    config = {"api_id": api_id, "region": REGION, "lambda_arns": lambda_arns, "endpoints": endpoints}
    path   = os.path.join(os.path.dirname(__file__), "..", "config.json")
    with open(path, "w") as f:
        json.dump(config, f, indent=2)
    print(f"\n  💾 Config saved → config.json")

def main():
    print("\n🚀 Starting deployment...\n")

    print("🔑 Fetching IAM Role...")
    role_arn = get_role_arn()

    print("\n📦 Deploying Lambda functions...")
    base        = os.path.dirname(__file__)
    lambda_arns = {}
    for name, rel_path in LAMBDAS.items():
        py_file = os.path.normpath(os.path.join(base, rel_path))
        lambda_arns[name] = deploy_lambda(name, py_file, role_arn)

    print("\n🌐 Creating API Gateway...")
    api_id = create_api(lambda_arns)

    print("\n📡 Deploying stages (dev / test / prod)...")
    endpoints = deploy_stages(api_id)
    save_config(api_id, lambda_arns, endpoints)

    print("\n✅ Deployment complete!\n" + "=" * 55)
    for stage, url in endpoints.items():
        print(f"  {stage.upper():5} → {url}")
    print("=" * 55 + "\n")

if __name__ == "__main__":
    main()
