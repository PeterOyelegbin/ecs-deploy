# Todo Web App
A todo web app built with tech stack such as: Django, HTML, Bootstrap, and MySQL.

In the course of development, I explored the object relational mapper (ORM), and django form, using a function based view with CRUD operations. The storage framework used are sqlite and MySQL during development.

This is one of my hands-on experience with Django, CRUD operations, database development, Web hosting and Docker.


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

6. Create ECS Cluster
    - For EC2 Launch Type:
    ```bash
    aws ecs create-cluster --cluster-name todo-cluster-ec2 \
    --capacity-providers FARGATE FARGATE_SPOT \
    --default-capacity-provider-strategy capacityProvider=FARGATE,weight=1 \
    --region us-east-1
    ```

    - For Fargate Launch Type (simpler):
    ```bash
    aws ecs create-cluster --cluster-name todo-cluster-fargate --region us-east-1
    ```

7. Create app secret in AWS Secret Manager


8. Create Task Definition
    - EC2 Task Definition (task-definition-ec2.json):
    ```bash
    {
        "family": "todo-task-ec2",
        "networkMode": "bridge",
        "executionRoleArn": "arn:aws:iam::ACCOUNT_ID:role/ecsTaskExecutionRole",
        "cpu": "256",
        "memory": "512",
        "requiresCompatibilities": ["EC2"],
        "containerDefinitions": [
            {
                "name": "todo-app-ec2",
                "image": "peteroyelegbin/todo-app:v1.0.0",
                "portMappings": [
                    {
                    "containerPort": 8000,
                    "hostPort": 0
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
                    "valueFrom": "arn:aws:secretsmanager:REGION:ACCOUNT_ID:secret:todo-app-S2oBvg:SECRET_KEY::"
                    },
                    {
                    "name": "DB_PASS",
                    "valueFrom": "arn:aws:secretsmanager:REGION:ACCOUNT_ID:secret:todo-app-S2oBvg:DB_PASS::"
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
    - Register EC2 task definitions:
    ```bash
    aws ecs register-task-definition \
        --cli-input-json file://$HOME/Documents/ecs/tasks/task-definition-ec2.json --region us-east-1
    ```

    ---

    - Fargate Task Definition (task-definition-fargate.json):
    ```bash
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
    - Register Fargate task definitions:
    ```bash
    aws ecs register-task-definition \
        --cli-input-json file://$HOME/Documents/ecs/tasks/task-definition-fargate.json --region us-east-1
    ```
    
9. Create Load Balancer & Target Group
    - Create Application Load Balancer
    ```bash
    aws elbv2 create-load-balancer \
        --name todo-alb \
        --subnets subnet-052cff93e26XXXXXX subnet-0d7c750e458XXXXXX \
        --security-groups sg-0c958aded09XXXXXX \
        --region us-east-1
    ```

    - Create target group
    ```bash
    aws elbv2 create-target-group \
        --name todo-tg \
        --protocol HTTP \
        --port 8000 \
        --target-type ip \
        --vpc-id vpc-016c892653bXXXXXX \
        --health-check-path /health/ \
        --region us-east-1
    ```

10. Add listener that forwards to a target group
```bash
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:REGION:ACCOUNT_ID:loadbalancer/app/todo-alb/75577a29XXXXX \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:REGION:ACCOUNT_ID:targetgroup/todo-tg/b661fefe1XXXXX
```

11. Create ECS Service
    - EC2 Service:
    ```bash
    aws ecs create-service \
        --cluster todo-cluster-ec2 \
        --service-name todo-service-ec2 \
        --task-definition todo-task-ec2:2 \
        --desired-count 2 \
        --launch-type EC2 \
        --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:us-east-1:226290659927:targetgroup/todo-tg/b661fefe18d2722f,containerName=todo-app-ec2,containerPort=8000" \
        --region us-east-1
    ```

    - Fargate Service:
    ```bash
    aws ecs create-service \
        --cluster todo-cluster-fargate \
        --service-name todo-service-fargate \
        --task-definition todo-task-fargate \
        --desired-count 2 \
        --launch-type FARGATE \
        --platform-version LATEST \
        --network-configuration "awsvpcConfiguration={subnets=[subnet-052cff93e26XXXXXX,subnet-0d7c750e458XXXXXX],securityGroups=[sg-0c958aded09XXXXXX],assignPublicIp=ENABLED}" \
        --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:REGION:ACCOUNT_ID:targetgroup/todo-tg/b661fefe18XXXXXX,containerName=todo-app-fargate,containerPort=8000" \
        --region us-east-1
    ```

## TODO: Deployment Automation using GitHub Actions Workflow
