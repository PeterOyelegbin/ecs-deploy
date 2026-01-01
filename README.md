# Deploy a Dockerize Todo Web App to Amazon ECS using Fargate (AWS CLI)
This guide walks through the end-to-end process of Dockerizing a Django application, and deploying the Docker image to Amazon Elastic Container Service (ECS) using the Fargate launch type, entirely with the AWS CLI.

## Prerequisites
Before you begin, ensure you have:
1. An AWS account
2. AWS CLI v2 installed and configured (aws configure)
3. Docker installed locally
4. An existing IAM user/role with permissions for:
    - ECS
    - EC2 (networking)
    - IAM
5. A default VPC (or note your custom VPC/subnet IDs)

## Architecture Overview
- Build a Docker image locally
- Push the image to Docker Hub
- Create an ECS cluster (Fargate)
- Register an ECS task definition
- Create an ECS service to run the task

---

## Docker Setup - Local Test
1. Rename .env_sample to .env

2. Start the Services
`docker-compose up -d`

3. Log Docker Service
`docker logs SERVICE_NAME`

4. Stop All Running Docker Containers
`docker-compose down`

5. Stop and Remove Containers + Volumes:
`docker-compose down -v`

6. Remove Orphan Containers and Unused Volumes:
```bash
docker system prune -a
docker system prune --volumes
```

---

## Delpoy to ECS
1. Build image
`docker build -t todo-app:v1.0.0 .`

2. Get Image ID
`docker images`

3. Test the built image
```bash
docker run -d -p 80:8000 \
  -e SECRET_KEY=your_app_secret \
  -e DEBUG=False \
  -e DB_HOST=your_db_host \
  -e DB_PORT=3306 \
  -e DB_NAME=your_db_name \
  -e DB_USER=your_db_user \
  -e DB_PASS=your_db_password \
  <IMAGE_ID>
```

4. Tag image
`docker tag todo-app:v1.0.0 dockerhub_username/todo-app:v1.0.0`

5. Push to Docker Hub
`docker push dockerhub_username/todo-app:v1.0.0`

6. Create an ECS Cluster (Fargate)
```bash
aws ecs create-cluster --cluster-name todo-cluster-fargate --region us-east-1
```

7. Create IAM Roles
Create Task Execution Role (if not existing)
    - First, create the trust policy file ecs-trust-policy.json:
    ```json
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "",
                "Effect": "Allow",
                "Principal": {
                    "Service": "ecs-tasks.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    ```
    - Then create and configure the role:
    ```bash
    # Create the role
    aws iam create-role --role-name ecsTaskExecutionRole \
        --assume-role-policy-document file://$HOME/ecs/ecs-trust-policy.json

    # Attach the managed policy
    aws iam attach-role-policy --role-name ecsTaskExecutionRole \
        --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy
    ```

8. Store Secrets in AWS Secrets Manager
Create a secret (example your App secret key and DB password):
```bash
aws secretsmanager create-secret --name todo-app-secrets \
    --secret-string '{"SECRET_KEY":"supersecret", "DB_PASS":"supersecret"}' \
    --region us-east-1
```
**Important:** Note the Secret ARN from the output. You'll need this for your task definition.

9. Create CloudWatch Log Group
```bash
aws logs create-log-group --log-group-name /ecs/todo-app --region us-east-1
```

10. Create Task Definition
    * First, create task-definition-fargate.json. Replace placeholders with your actual values:
        - ACCOUNT_ID: Your AWS account ID
        - REGION: AWS region (e.g., us-east-1)
        - SECRET_NAME: Your secret name (e.g., todo-app-secrets)
    ```json
    {
        "family": "todo-task-fargate",
        "networkMode": "awsvpc",
        "executionRoleArn": "arn:aws:iam::ACCOUNT_ID:role/ecsTaskExecutionRole",
        "taskRoleArn": "arn:aws:iam::ACCOUNT_ID:role/ecsTaskExecutionRole",
        "cpu": "256",
        "memory": "512",
        "requiresCompatibilities": ["FARGATE"],
        "containerDefinitions": [
            {
                "name": "todo-app-fargate",
                "image": "peteroyelegbin/todo-app:v1.0.0",
                "portMappings": [
                    {
                    "containerPort": 8000,
                    "protocol": "tcp"
                    }
                ],
                "environment": [
                    {
                    "name": "DEBUG",
                    "value": "False"
                    },
                    {
                    "name": "DB_HOST",
                    "value": "db4free.net"
                    },
                    {
                    "name": "DB_PORT",
                    "value": "3306"
                    },
                    {
                    "name": "DB_USER",
                    "value": "peter_oyelegbin"
                    },
                    {
                    "name": "DB_NAME",
                    "value": "todo_django"
                    }
                ],
                "secrets": [
                    {
                    "name": "SECRET_KEY",
                    "valueFrom": "arn:aws:secretsmanager:REGION:ACCOUNT_ID:secret:SECRET_NAME:SECRET_KEY::"
                    },
                    {
                    "name": "DB_PASS",
                    "valueFrom": "arn:aws:secretsmanager:REGION:ACCOUNT_ID:secret:SECRET_NAME:DB_PASS::"
                    }
                ],
                "logConfiguration": {
                    "logDriver": "awslogs",
                    "options": {
                    "awslogs-group": "/ecs/todo-app",
                    "awslogs-region": "us-east-1",
                    "awslogs-stream-prefix": "ecs"
                    }
                }
            }
        ]
    }
    ```
    - Register the task definitions:
    ```bash
    aws ecs register-task-definition \
        --cli-input-json file://$HOME/ecs/task-definition-fargate.json --region us-east-1
    ```

11. Create Security Groups
    - First, get your VPC ID:
    ```bash
    aws ec2 describe-vpcs --filters "Name=is-default,Values=true" --query "Vpcs[0].VpcId" --output text
    ```

    - ALB Security Group
    ```bash
    # Create ALB security group
    aws ec2 create-security-group --group-name alb-sg \
        --description "ALB security group" --vpc-id <YOUR_VPC_ID> \
        --region us-east-1 --query 'GroupId' --output text
    
    # Allow HTTP inbound (adjust for HTTPS if using SSL)
    aws ec2 authorize-security-group-ingress --group-id <ALB_SG_ID> \
        --protocol tcp --port 80 --cidr 0.0.0.0/0 --region us-east-1
    ```
    
    - ECS Task Security Group
    ```bash
    # Create ECS task security group
    aws ec2 create-security-group --group-name ecs-task-sg \
        --description "ECS task security group" --vpc-id <YOUR_VPC_ID> \
        --region us-east-1 --query 'GroupId' --output text

    # Allow traffic from ALB only:
    aws ec2 authorize-security-group-ingress --group-id <TASK_SG_ID> \
        --protocol tcp --port 8000 --source-group <ALB_SG_ID> --region us-east-1
    ```

12. Create Load Balancer & Target Group
    - Get your subnet IDs:
    ```bash
    aws ec2 describe-subnets --filters "Name=vpc-id,Values=<YOUR_VPC_ID>" --query "Subnets[*].SubnetId" --output text
    ```
    
    - Create Application Load Balancer
    ```bash
    aws elbv2 create-load-balancer --name todo-alb \
        --subnets subnet-XXXXXX subnet-YYYYYY \
        --security-groups <ALB_SG_ID> \
        --scheme internet-facing --type application --region us-east-1 \
        --query 'LoadBalancers[0].LoadBalancerArn' --output text
    ```

    - Create target group
    ```bash
    aws elbv2 create-target-group --name todo-tg --protocol HTTP \
        --port 8000 --target-type ip --vpc-id <YOUR_VPC_ID> \
        --health-check-path /health/ --health-check-interval-seconds 30 \
        --health-check-timeout-seconds 5 --healthy-threshold-count 2 \
        --unhealthy-threshold-count 2 --region us-east-1 \
        --query 'TargetGroups[0].TargetGroupArn' --output text
    ```

13. Add listener that forwards to a target group
```bash
aws elbv2 create-listener \
  --load-balancer-arn <ALB_ARN> \
  --protocol HTTP --port 80 \
  --default-actions Type=forward,TargetGroupArn=TG_ARN \
  --region us-east-1
```

14. Create ECS Service
```bash
aws ecs create-service --cluster todo-cluster-fargate \
    --service-name todo-service-fargate --task-definition todo-task-fargate \
    --desired-count 2 --launch-type FARGATE --platform-version LATEST \
    --network-configuration "awsvpcConfiguration={subnets=[subnet-XXXXXX,subnet-YYYYYY],securityGroups=[<TASK_SG_ID>],assignPublicIp=ENABLED}" \
    --load-balancers "targetGroupArn=<TG_ARN>,containerName=todo-app-fargate,containerPort=8000" \
    --region us-east-1
```

---

## Important Notes:
1. Replace placeholders (XXXXXX, YOUR_VPC_ID, ACCOUNT_ID, TASK_SG_ID, TG_ARN, etc.) with your actual values
2. The task needs internet access to reach external database. Consider using RDS or another managed database for production
3. For production, use HTTPS (port 443) instead of HTTP (port 80)
4. Consider adding auto-scaling configuration
5. Ensure your subnets are in different Availability Zones for high availability

---

## Cleanup (Optional)
```bash
# Delete service
aws ecs delete-service --cluster todo-cluster-fargate \
    --service todo-service-fargate --force --region us-east-1

# Wait for service to be deleted, then delete cluster
aws ecs delete-cluster --cluster todo-cluster-fargate --region us-east-1

# Delete ALB
aws elbv2 delete-load-balancer --load-balancer-arn <ALB_ARN> --region us-east-1

# Delete target group
aws elbv2 delete-target-group --target-group-arn <TG_ARN> --region us-east-1

# Delete security groups
aws ec2 delete-security-group --group-id <TASK_SG_ID> --region us-east-1

aws ec2 delete-security-group --group-id <ALB_SG_ID> --region us-east-1

# Delete log group
aws logs delete-log-group --log-group-name /ecs/todo-app --region us-east-1
```

---

## TODO:
1. Deployment Automation using GitHub Actions Workflow
2. Provide a Terraform version

---

## Conclusion
You have successfully deployed a Docker container to Amazon ECS using the Fargate launch type via the AWS CLI, without managing servers. This setup is ideal for production-ready, scalable container workloads.
