.PHONY: help validate deploy status delete logs

# Configuration
STACK_NAME = serverless-api-stack
REGION = us-east-1
TEMPLATE = template.yaml

# Aide
help:
	@echo "📋 Commandes disponibles:"
	@echo ""
	@echo "  make validate  - Valider le template CloudFormation"
	@echo "  make deploy    - Déployer l'infrastructure"
	@echo "  make status    - Vérifier le statut de la stack"
	@echo "  make logs      - Voir les événements"
	@echo "  make delete    - Supprimer la stack"
	@echo ""

# Valider le template
validate:
	@echo "✓ Validating template..."
	python3 scripts/validate.py $(TEMPLATE)

# Déployer
deploy: validate
	@echo "🚀 Deploying stack..."
	aws cloudformation deploy \
		--template-file $(TEMPLATE) \
		--stack-name $(STACK_NAME) \
		--capabilities CAPABILITY_IAM \
		--region $(REGION) \
		--no-fail-on-empty-changeset
	@echo "✅ Deployment complete!"

# Statut
status:
	@aws cloudformation describe-stacks \
		--stack-name $(STACK_NAME) \
		--query 'Stacks[0].[StackName,StackStatus,CreationTime]' \
		--output table \
		--region $(REGION) 2>/dev/null || echo "Stack not found"

# Logs
logs:
	@aws cloudformation describe-stack-events \
		--stack-name $(STACK_NAME) \
		--region $(REGION) \
		--query 'StackEvents[*].[Timestamp,LogicalResourceId,ResourceStatus]' \
		--output table 2>/dev/null || echo "No events found"

# Supprimer
delete:
	@echo "🗑️ Deleting stack..."
	aws cloudformation delete-stack \
		--stack-name $(STACK_NAME) \
		--region $(REGION)
	@echo "✅ Deletion initiated"
