# AWS API Gateway + Lambda — Projet Multi-Stage

## Architecture
GitHub (main/test/develop)
│
▼
GitHub Actions CI/CD
│
├── Lint (flake8)
└── Deploy (boto3)
│
▼
API Gateway (REST)
├── /data    → Lambda data-handler
├── /images  → Lambda image-processor
└── /users   → Lambda user-manager
│
▼
3 Stages : dev / test / prod

## Services AWS utilisés

| Service | Rôle |
|---------|------|
| AWS Lambda | Fonctions serverless (Python 3.10) |
| API Gateway | Point d'entrée REST multi-stage |
| IAM | Rôle d'exécution LambdaExecutionRole |
| CloudWatch | Logs automatiques des Lambdas |

## Structure du projet
aws-api-project/
├── lambdas/
│   ├── data_handler/        # CRUD données
│   ├── image_processor/     # Traitement d'images
│   └── user_manager/        # Gestion utilisateurs
├── scripts/
│   ├── deploy.py            # Déploiement AWS via boto3
│   └── test_api.py          # Tests des endpoints
├── .github/
│   └── workflows/
│       └── cicd.yml         # Pipeline CI/CD
├── requirements.txt
└── config.json              # Généré au déploiement

## Endpoints

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/data` | Liste les données |
| POST | `/data` | Crée un item |
| PUT | `/data` | Met à jour un item |
| DELETE | `/data` | Supprime un item |
| POST | `/images` | Analyse/resize/thumbnail |
| GET | `/users` | Liste les utilisateurs |
| POST | `/users` | Crée un utilisateur |
| PUT | `/users` | Met à jour un utilisateur |
| DELETE | `/users` | Supprime un utilisateur |

## Stages

| Stage | Branche Git | URL |
|-------|-------------|-----|
| dev | develop | `https://{api_id}.execute-api.us-east-1.amazonaws.com/dev` |
| test | test | `https://{api_id}.execute-api.us-east-1.amazonaws.com/test` |
| prod | main | `https://{api_id}.execute-api.us-east-1.amazonaws.com/prod` |

> Le stage **prod** a le cache API Gateway activé (0.5 GB, TTL 300s).

## CI/CD

Le pipeline GitHub Actions se déclenche automatiquement à chaque push :

1. **Lint** — vérifie la qualité du code avec flake8
2. **Deploy** — déploie les Lambdas et l'API Gateway via boto3
3. **Test** — exécute les tests HTTP sur le stage correspondant
4. **Artifact** — sauvegarde config.json avec les URLs

## Déploiement manuel

```bash
# Installer les dépendances
pip install -r requirements.txt

# Déployer
python scripts/deploy.py

# Tester
python scripts/test_api.py dev
python scripts/test_api.py test
python scripts/test_api.py prod
```

## Reconfigurer les credentials (Whizlabs sandbox)

A chaque nouvelle session sandbox, mettre à jour `~/.aws/credentials` :

```ini
[default]
aws_access_key_id=VOTRE_ACCESS_KEY
aws_secret_access_key=VOTRE_SECRET_KEY
```

Puis recréer le rôle si la sandbox est nouvelle :

```bash
aws iam create-role \
  --role-name LambdaExecutionRole \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "lambda.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }'

aws iam attach-role-policy \
  --role-name LambdaExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
```

Et mettre à jour les secrets GitHub (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`).
