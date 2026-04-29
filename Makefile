STACK_NAME = MissionStack
REGION = us-east-1
S3_BUCKET = $(shell aws s3 ls | head -n 1 | cut -d' ' -f3)

.PHONY: package deploy

# 1. Envoyer les zips sur S3 (Obligatoire pour CloudFormation)
package:
	aws s3 cp get_products.zip s3://$(S3_BUCKET)/
	aws s3 cp manage_users.zip s3://$(S3_BUCKET)/
	aws s3 cp process_image.zip s3://$(S3_BUCKET)/

# 2. Déployer l'infrastructure
deploy: package
	aws cloudformation deploy \
		--template-file template.json \
		--stack-name $(STACK_NAME) \
		--capabilities CAPABILITY_IAM \
		--parameter-overrides BucketName=$(S3_BUCKET) \
		--region $(REGION)

# 3. Supprimer tout si besoin
clean:
	aws cloudformation delete-stack --stack-name $(STACK_NAME)