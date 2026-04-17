# AWS Deployment Guide

This document provides step-by-step instructions for deploying the Inflation Sentiment Engine to AWS.

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│ AWS Account                                                  │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ CloudWatch Events (Trigger)                            │ │
│  │ Schedule: Every 6 hours                                │ │
│  └────────────────────────────────────────────────────────┘ │
│                          │                                   │
│                          ▼                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Lambda Function: inflation-sentiment-engine            │ │
│  │ Runtime: Python 3.11                                   │ │
│  │ Memory: 1024 MB, Timeout: 300s                        │ │
│  └────────────────────────────────────────────────────────┘ │
│                          │                                   │
│         ┌────────────────┼────────────────┐                │
│         │                │                │                │
│         ▼                ▼                ▼                │
│   ┌──────────┐   ┌──────────────┐   ┌──────────┐          │
│   │ NewsAPI  │   │ Twitter API  │   │ Internet │          │
│   │ (Public) │   │ (Public)     │   │ (Egress) │          │
│   └──────────┘   └──────────────┘   └──────────┘          │
│                          │                                   │
│         ┌────────────────┘                                  │
│         │                                                    │
│         ▼                                                    │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ VPC                                                    │ │
│  │ ┌──────────────────────────────────────────────────┐  │ │
│  │ │ RDS PostgreSQL: inflation-sentiment-db          │  │ │
│  │ │ Multi-AZ, Automated Backups, Encryption         │  │ │
│  │ └──────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────┘ │
│                          │                                   │
│                          ▼                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Optional: ECS/Fargate for MCP Server                  │ │
│  │ (Load balanced, auto-scaling)                         │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

## Prerequisites

- AWS Account with appropriate permissions
- AWS CLI configured with credentials
- Python 3.11+
- Docker (for containerization)

## Step 1: Create IAM Role for Lambda

```bash
# Create trust policy document
cat > lambda-trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Create role
aws iam create-role \
  --role-name inflation-sentiment-lambda-role \
  --assume-role-policy-document file://lambda-trust-policy.json

# Attach policies
aws iam attach-role-policy \
  --role-name inflation-sentiment-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole

aws iam attach-role-policy \
  --role-name inflation-sentiment-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/CloudWatchLogsFullAccess
```

## Step 2: Create RDS PostgreSQL Database

```bash
# Create security group for RDS
aws ec2 create-security-group \
  --group-name inflation-sentiment-rds-sg \
  --description "Security group for sentiment RDS"

# Get security group ID
SG_ID=$(aws ec2 describe-security-groups \
  --filters "Name=group-name,Values=inflation-sentiment-rds-sg" \
  --query 'SecurityGroups[0].GroupId' \
  --output text)

# Create RDS instance
aws rds create-db-instance \
  --db-instance-identifier inflation-sentiment-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version 15.2 \
  --master-username sentiment_admin \
  --master-user-password ChangeMe_SecurePassword123 \
  --allocated-storage 20 \
  --storage-type gp3 \
  --vpc-security-group-ids $SG_ID \
  --backup-retention-period 7 \
  --multi-az \
  --enable-cloudwatch-logs-exports postgresql

# Wait for database creation (takes ~15 minutes)
aws rds wait db-instance-available \
  --db-instance-identifier inflation-sentiment-db
```

## Step 3: Create Lambda Layer for Dependencies

```bash
# Create directory structure
mkdir -p lambda_layer/python

# Install dependencies
pip install -r requirements.txt -t lambda_layer/python/

# Create ZIP
cd lambda_layer
zip -r ../lambda_layer.zip .
cd ..

# Create Lambda layer
LAYER_ARN=$(aws lambda publish-layer-version \
  --layer-name inflation-sentiment-dependencies \
  --zip-file fileb://lambda_layer.zip \
  --compatible-runtimes python3.11 \
  --query 'LayerVersionArn' \
  --output text)

echo "Layer ARN: $LAYER_ARN"
```

## Step 4: Package Lambda Function

```bash
# Create deployment package
mkdir -p lambda_deployment
cp -r config database scrapers sentiment utils lambda_deployment/
cp aws_lambda/handler.py lambda_deployment/
cp requirements.txt lambda_deployment/

# Create ZIP
cd lambda_deployment
zip -r ../lambda_function.zip .
cd ..
```

## Step 5: Create Lambda Function

```bash
# Get RDS endpoint
DB_ENDPOINT=$(aws rds describe-db-instances \
  --db-instance-identifier inflation-sentiment-db \
  --query 'DBInstances[0].Endpoint.Address' \
  --output text)

# Create Lambda function
LAMBDA_ARN=$(aws lambda create-function \
  --function-name inflation-sentiment-engine \
  --runtime python3.11 \
  --role arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/inflation-sentiment-lambda-role \
  --handler aws_lambda.handler.lambda_handler \
  --zip-file fileb://lambda_function.zip \
  --timeout 300 \
  --memory-size 1024 \
  --environment Variables="{
    DATABASE_URL=postgresql://sentiment_admin:ChangeMe_SecurePassword123@$DB_ENDPOINT:5432/inflation_sentiment,
    TWITTER_BEARER_TOKEN=your_bearer_token,
    NEWS_API_KEY=your_news_api_key,
    SENTIMENT_MODEL=ProsusAI/finbert,
    DEVICE=cpu
  }" \
  --layers $LAYER_ARN \
  --query 'FunctionArn' \
  --output text)

echo "Lambda ARN: $LAMBDA_ARN"
```

## Step 6: Initialize Database

```bash
# Get Lambda function URL
LAMBDA_INVOCATION_ROLE=$(aws iam list-roles \
  --query 'Roles[?RoleName==`inflation-sentiment-lambda-role`].Arn' \
  --output text)

# Create test invoke script
cat > init_db.py <<'EOF'
import sys
sys.path.insert(0, 'lambda_deployment')

from config import get_settings
from database import init_db

settings = get_settings()
init_db(settings.database_url)
print("Database initialized successfully!")
EOF

# Run initialization (locally or in Lambda)
python init_db.py
```

## Step 7: Create CloudWatch Events Trigger

```bash
# Create EventBridge rule (every 6 hours)
aws events put-rule \
  --name inflation-sentiment-schedule \
  --schedule-expression "rate(6 hours)" \
  --state ENABLED

# Get Lambda ARN
LAMBDA_ARN=$(aws lambda list-functions \
  --query 'Functions[?FunctionName==`inflation-sentiment-engine`].FunctionArn' \
  --output text)

# Add Lambda as target
aws events put-targets \
  --rule inflation-sentiment-schedule \
  --targets "Id"="1","Arn"="$LAMBDA_ARN","RoleArn"="arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/service-role/EventBridgeInvokeRole"

# Allow EventBridge to invoke Lambda
aws lambda add-permission \
  --function-name inflation-sentiment-engine \
  --statement-id AllowEventBridgeInvoke \
  --action lambda:InvokeFunction \
  --principal events.amazonaws.com \
  --source-arn arn:aws:events:us-east-1:$(aws sts get-caller-identity --query Account --output text):rule/inflation-sentiment-schedule
```

## Step 8: Deploy MCP Server (Optional)

### Option A: Using ECS Fargate

```bash
# Create ECR repository
aws ecr create-repository \
  --repository-name inflation-sentiment-mcp

# Build and push Docker image
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com

docker build -t inflation-sentiment-mcp:latest .
docker tag inflation-sentiment-mcp:latest $(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com/inflation-sentiment-mcp:latest
docker push $(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com/inflation-sentiment-mcp:latest

# Create ECS task definition, service, etc. (see AWS ECS documentation)
```

### Option B: Using API Gateway + Lambda

```bash
# Create REST API
aws apigateway create-rest-api \
  --name inflation-sentiment-api \
  --description "MCP API for sentiment queries"

# Create Lambda proxy integration
# (See AWS API Gateway documentation for detailed setup)
```

## Step 9: Monitor and Troubleshoot

### View Lambda Logs

```bash
# Get latest logs
aws logs tail /aws/lambda/inflation-sentiment-engine --follow
```

### Test Lambda Manually

```bash
# Invoke Lambda function
aws lambda invoke \
  --function-name inflation-sentiment-engine \
  --payload '{}' \
  response.json

# View response
cat response.json
```

### Check RDS Database

```bash
# Connect to RDS (from EC2 instance or local with VPN)
psql -h $DB_ENDPOINT -U sentiment_admin -d inflation_sentiment

# List tables
\dt

# Check data
SELECT COUNT(*) FROM articles;
SELECT COUNT(*) FROM sentiment_analysis;
```

## Step 10: Production Hardening

### Security Enhancements

```bash
# 1. Use AWS Secrets Manager for credentials
aws secretsmanager create-secret \
  --name inflation-sentiment/db-password \
  --secret-string "your-secure-password"

# 2. Enable VPC endpoints for private connectivity
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-xxxxx \
  --service-name com.amazonaws.us-east-1.s3 \
  --route-table-ids rtb-xxxxx

# 3. Enable RDS encryption
aws rds modify-db-instance \
  --db-instance-identifier inflation-sentiment-db \
  --storage-encrypted \
  --kms-key-id arn:aws:kms:us-east-1:xxxxx:key/xxxxx \
  --apply-immediately
```

### Monitoring and Alarms

```bash
# Create CloudWatch alarm for Lambda errors
aws cloudwatch put-metric-alarm \
  --alarm-name inflation-sentiment-lambda-errors \
  --alarm-description "Alert when Lambda has errors" \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --statistic Sum \
  --period 300 \
  --threshold 5 \
  --comparison-operator GreaterThanThreshold \
  --alarm-actions arn:aws:sns:us-east-1:xxxxx:alert-topic
```

## Cost Estimation

### Monthly Costs (Approximate)

| Service | Usage | Cost |
|---------|-------|------|
| Lambda | 240 invocations (10/day) | $0.20 |
| RDS | db.t3.micro multi-AZ | $35 |
| Data Transfer | ~100GB/month | $15 |
| CloudWatch Logs | ~10GB/month | $5 |
| **Total** | | **~$55/month** |

## Cleanup (To Delete Resources)

```bash
# Delete Lambda function
aws lambda delete-function --function-name inflation-sentiment-engine

# Delete RDS instance
aws rds delete-db-instance \
  --db-instance-identifier inflation-sentiment-db \
  --skip-final-snapshot

# Delete IAM role
aws iam detach-role-policy \
  --role-name inflation-sentiment-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole

aws iam delete-role --role-name inflation-sentiment-lambda-role

# Delete EventBridge rule
aws events remove-targets --rule inflation-sentiment-schedule --ids "1"
aws events delete-rule --name inflation-sentiment-schedule
```

## Troubleshooting

### Common Issues

1. **Lambda Timeout**
   - Increase timeout to 900 seconds
   - Consider splitting pipeline into multiple functions

2. **Database Connection Errors**
   - Check security group rules
   - Verify database is accessible from Lambda VPC
   - Check credentials in environment variables

3. **API Rate Limiting**
   - Implement exponential backoff in scrapers
   - Use RequestID for tracking
   - Consider API pagination

4. **Out of Memory**
   - Increase Lambda memory
   - Process articles in smaller batches
   - Implement streaming for large result sets

## Next Steps

1. Configure automated backups and disaster recovery
2. Set up CI/CD pipeline with CodePipeline
3. Implement custom metrics dashboard in CloudWatch
4. Create SNS topics for error alerts
5. Document runbooks for operational support

---

For questions or issues, contact the Data Engineering team.
