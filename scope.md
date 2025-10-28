# Project Scope and Purpose

## What This Project Is

A template that deploys a simple Python API to AWS so you can:
1. Write a FastAPI app (in `app/`)
2. Press a button to deploy to AWS (using `make deploy` or a GitHub Actions workflow)
3. Get a public URL automatically

## What You Get

A containerized FastAPI app running on AWS behind a load balancer, with autoscaling, logging, and monitoring.

## Simple Flow

```
Your Python App (app/main.py)
    ↓
Docker Container
    ↓  
AWS Fargate (Serverless Container Service)
    ↓
Load Balancer (Public URL)
    ↓
Anyone can access it via HTTP
```

## Quick Start (3 Commands)

```bash
# 1. Install dependencies
pip install -r deploy/cdk/requirements.txt

# 2. Bootstrap AWS (first time only)
cd deploy/cdk && cdk bootstrap

# 3. Deploy everything
cdk deploy
```

That's it. AWS provisions: networking, a load balancer, containers, autoscaling, and monitoring.

## What This Solves

- I need to deploy a Python API.
- I want it to scale automatically.
- I want it monitored.
- I want to deploy with a single command (CDK/CDK CLI or via GitHub Actions).

## Real-World Use

You have a FastAPI service and want a production-ready AWS setup without writing CloudFormation or Terraform.
