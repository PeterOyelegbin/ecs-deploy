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
`docker build -t todo-app .`

2. Tag image
`docker tag todo-app:v1.0.0 peteroyelegbin/todo-app:v1.0.0`

3. Push to Docker Hub
`docker push peteroyelegbin/todo-app:v1.0.0`

4. Create ECS Cluster
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

5. Create Task Definition
    - EC2 Task Definition (task-definition-ec2.json):
    ```bash
    {
        "family": "django-task-ec2",
        "networkMode": "bridge",
        "cpu": "256",
        "memory": "512",
        "requiresCompatibilities": ["EC2"],
        "containerDefinitions": [
            {
            "name": "django-container",
            "image": "ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/django-app:latest",
            "portMappings": [
                {
                "containerPort": 8000,
                "hostPort": 0
                }
            ],
            "environment": [...],
            "logConfiguration": {...}
            }
        ]
    }
    ```
    - Register EC2 task definitions:
    ```bash
    aws ecs register-task-definition \
        --cli-input-json file://task-definition-ec2.json --region us-east-1
    ```

    ---

    - Fargate Task Definition (task-definition-fargate.json):
    ```bash
    {
        "family": "django-task-fargate",
        "networkMode": "awsvpc",
        "executionRoleArn": "arn:aws:iam::ACCOUNT_ID:role/ecsTaskExecutionRole",
        "taskRoleArn": "arn:aws:iam::ACCOUNT_ID:role/ecsTaskRole",
        "cpu": "256",
        "memory": "512",
        "requiresCompatibilities": ["FARGATE"],
        "containerDefinitions": [
            {
            "name": "django-container",
            "image": "ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/django-app:latest",
            "portMappings": [
                {
                "containerPort": 8000,
                "protocol": "tcp"
                }
            ],
            "environment": [
                {
                "name": "DATABASE_URL",
                "value": "postgresql://admin:password@django-db.xxxxxx.us-east-1.rds.amazonaws.com:5432/django_db"
                },
                {
                "name": "DJANGO_SECRET_KEY",
                "value": "your-secret-key"
                },
                {
                "name": "DEBUG",
                "value": "False"
                }
            ],
            "secrets": [
                {
                "name": "DATABASE_PASSWORD",
                "valueFrom": "arn:aws:secretsmanager:region:account-id:secret:secret-name"
                }
            ],
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                "awslogs-group": "/ecs/django-app",
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
        --cli-input-json file://task-definition-fargate.json --region us-east-1
    ```
    