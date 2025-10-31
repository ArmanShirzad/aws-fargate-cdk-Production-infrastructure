# Production-Ready AWS Infrastructure with CDK

A comprehensive AWS infrastructure project deploying containerized APIs to ECS Fargate using Infrastructure as Code. Designed for scalable AI/ML model serving, microservices, and production workloads.

## Use Case: AI/ML Model Deployment

This infrastructure is optimized for deploying AI/ML APIs in production:
- **Scalability**: Auto-scaling Fargate tasks handle varying inference loads
- **Reliability**: Multi-AZ deployment ensures high availability
- **Security**: Secrets Manager integration for API keys, model artifacts
- **Observability**: CloudWatch dashboards track latency, errors, throughput
- **Zero-Downtime**: Blue/green deployment support for model updates

## What This Demonstrates

### AWS Services & Best Practices
- **ECS Fargate**: Serverless container orchestration
- **Application Load Balancer**: Traffic distribution and health checks
- **VPC Networking**: Multi-AZ architecture with public/private subnets
- **CloudWatch**: Logging, metrics, and custom dashboards
- **Secrets Manager**: Secure credential management
- **SSM Parameter Store**: Configuration management
- **CodeDeploy**: Blue/green deployment strategies
- **IAM**: OIDC authentication, permissions boundaries, least privilege
- **Infrastructure as Code**: AWS CDK with Python
- **CI/CD**: GitHub Actions with secure AWS integration

### Engineering Excellence
- Infrastructure as Code with AWS CDK
- Automated testing and deployment pipelines
- Security-first approach with OIDC and least privilege
- Production-grade observability and monitoring
- Cost-optimized auto-scaling policies
- GitOps workflow with GitHub Actions

## Architecture Overview

### System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         GitHub Actions                           │
│  (OIDC Authentication for AWS via IAM Role)                      │
└────────────────────┬────────────────────────────────────────────┘
                     │ Triggered on: push to main, workflow_dispatch
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CDK Deployment Pipeline                       │
│  • Checkout code                                                 │
│  • Configure AWS credentials (OIDC)                              │
│  • Install Python & CDK dependencies                             │
│  • Run cdk diff                                                  │
│  • Run cdk deploy                                                │
└────────────────────┬────────────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AWS Cloud Resources                           │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Application Load Balancer (Internet-facing)             │   │
│  │  • Port 80: Production listener                           │   │
│  │  • Port 9001: Test/Canary listener (internal)           │   │
│  └────────────┬────────────────────┬────────────────────────┘   │
│               │                     │                             │
│               ▼                     ▼                             │
│  ┌──────────────────────┐  ┌──────────────────────┐            │
│  │ Production           │  │ Canary               │            │
│  │ Target Group         │  │ Target Group         │            │
│  │ (default routing)    │  │ (test/blue-green)    │            │
│  └──────────┬───────────┘  └──────────┬───────────┘            │
│             │                         │                         │
│             └────────────┬────────────┘                         │
│                          ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              ECS Fargate Service                         │  │
│  │  • Task Definition: Python 3.11, 512 CPU, 1024 MB       │  │
│  │  • Auto Scaling: 1-5 tasks (CPU + request-based)         │  │
│  │  • Health Check: /healthz endpoint                       │  │
│  │                                                           │  │
│  │  ┌─────────────────────────────────────────────────┐    │  │
│  │  │  Application Container                           │    │  │
│  │  │  • FastAPI Service (port 8000)                  │    │  │
│  │  │  • Environment: SERVICE_NAME                     │    │  │
│  │  │  • Secrets: APP_SECRET (Secrets Manager)         │    │  │
│  │  │  • Logs: CloudWatch Logs                          │    │  │
│  │  └─────────────────────────────────────────────────┘    │  │
│  │                                                           │  │
│  │  ┌─────────────────────────────────────────────────┐    │  │
│  │  │  Optional: ADOT Collector Sidecar              │    │  │
│  │  │  • OpenTelemetry metrics & traces               │    │  │
│  │  │  • Port 4317 (OTLP)                             │    │  │
│  │  └─────────────────────────────────────────────────┘    │  │
│  └────────┬──────────────────────────┬───────────────────────┘  │
│           │                          │                          │
│           │                          │                          │
│           ▼                          ▼                          │
│  ┌────────────────────────┐  ┌───────────────────────────┐    │
│  │  Private Subnets       │  │  Public Subnets            │    │
│  │  (3 Availability Zones) │  │  (for ALB)                 │    │
│  └────────┬───────────────┘  └────────┬──────────────────┘    │
│           │                          │                          │
│           └──────────┬───────────────┘                          │
│                      ▼                                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  VPC with Flow Logs                                       │  │
│  │  • 3 Availability Zones                                  │  │
│  │  • Public Subnets (ALB)                                  │  │
│  │  • Private Subnets with NAT (ECS tasks)                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  Observability Layer                                     │  │
│  │  • CloudWatch Logs (30-day retention)                   │  │
│  │  • CloudWatch Dashboard (CPU, Request Count)            │  │
│  │  • VPC Flow Logs                                        │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  Optional: Blue/Green Deployment (CodeDeploy)           │  │
│  │  • Application: ECS-{cluster}-{service}                 │  │
│  │  • Deployment Config: 10% canary, 5min wait             │  │
│  │  • Blue: Production Target Group                        │  │
│  │  • Green: Canary Target Group                           │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  IAM & Access Control                                    │  │
│  │  • Permissions Boundary (deployment limits)              │  │
│  │  • GitHub OIDC Role (no long-lived keys)                │  │
│  │  • Task Role (SSM, Secrets, CloudWatch)                │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  Configuration & Secrets                                 │  │
│  │  • Secrets Manager: /{service-name}/app                 │  │
│  │  • SSM Parameter Store: /{service-name}/example-config │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Deployment Workflow

```
┌──────────────────┐
│  Developer       │
│  (Local Machine) │
└────────┬─────────┘
         │
         │ git push origin main
         ▼
┌──────────────────────────────────────────────────────────────┐
│  GitHub Repository                                           │
│  • FastAPI app in app/                                       │
│  • CDK stacks in deploy/cdk/                                 │
│  • GitHub Actions workflow                                    │
└────────┬─────────────────────────────────────────────────────┘
         │
         │ Push event triggers workflow
         ▼
┌──────────────────────────────────────────────────────────────┐
│  GitHub Actions Runner (Ubuntu)                              │
│                                                               │
│  1. Checkout code                                            │
│  2. Configure AWS credentials via OIDC                      │
│     - Assume IAM role (no AWS keys stored)                  │
│  3. Setup Python 3.11                                       │
│  4. Install CDK deps:                                        │
│     pip install -r deploy/cdk/requirements.txt              │
│  5. Run CDK diff (shows planned changes)                    │
│  6. Run CDK deploy                                           │
│     cd deploy/cdk                                            │
│     cdk deploy --require-approval never                      │
└────────┬─────────────────────────────────────────────────────┘
         │
         │ CDK synthesizes CloudFormation templates
         ▼
┌──────────────────────────────────────────────────────────────┐
│  AWS CloudFormation                                          │
│  Stack: {service-name}-stack                                 │
│                                                               │
│  Deployment Steps:                                           │
│  1. Create VPC (3 AZs, public/private subnets)              │
│  2. Create ALB with target groups                           │
│  3. Create ECS cluster & task definition                    │
│  4. Create Fargate service with auto scaling               │
│  5. Create CodeDeploy application (optional)                │
│  6. Create IAM roles & permissions                          │
│  7. Create CloudWatch dashboard                             │
│  8. Build & push Docker image                               │
└────────┬─────────────────────────────────────────────────────┘
         │
         │ Stack deployment completes
         ▼
┌──────────────────────────────────────────────────────────────┐
│  Outputs                                                     │
│  • LoadBalancerDNS: {alb-dns-name}                           │
│  • DeployRoleArn: {iam-role-arn}                             │
└──────────────────────────────────────────────────────────────┘
         │
         │ Users can access service
         ▼
┌──────────────────────────────────────────────────────────────┐
│  End Users                                                   │
│  • HTTP: http://{alb-dns-name}/                              │
│  • Health: http://{alb-dns-name}/healthz                     │
└──────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

```
Request Flow:
Internet User
    │
    ▼ HTTP Request
Application Load Balancer (Port 80)
    │
    ▼ Health Check /healthz
Production Target Group
    │
    ▼ Route to healthy task
ECS Fargate Task (Private Subnet)
    │
    ├─ FastAPI Container (Port 8000)
    │    ├─ Read APP_SECRET from Secrets Manager
    │    ├─ Read config from SSM Parameter Store
    │    ├─ Log to CloudWatch Logs
    │    └─ Send metrics to CloudWatch
    │
    └─ ADOT Collector (optional, Port 4317)
         └─ Send traces to X-Ray/CloudWatch

Auto Scaling Flow:
CloudWatch Metrics
    │
    ├─ CPU Utilization > 55% → Scale Up
    └─ Request Count > 1000 per target → Scale Up

Blue/Green Deployment Flow (if enabled):
GitHub Actions Trigger
    │
    ▼ CDK Deploy
ECS CodeDeploy Application
    │
    ├─ Deploy 10% traffic to canary
    │   │ (5-minute wait period)
    │   ▼
    ├─ Monitor health checks
    │   ▼
    ├─ Deploy 100% traffic to production
    │   ▼
    └─ Terminate old tasks after 5 minutes
```

## Technology Stack

- **Infrastructure**: AWS CDK v2 (Python)
- **Container Orchestration**: Amazon ECS Fargate
- **Load Balancing**: Application Load Balancer
- **Networking**: VPC with multi-AZ subnets
- **Monitoring**: CloudWatch Logs, Metrics, Dashboards
- **Security**: IAM, Secrets Manager, SSM Parameter Store
- **CI/CD**: GitHub Actions with OIDC
- **Container Runtime**: Docker
- **Application Framework**: FastAPI (Python 3.11)

## Repository Layout

```
.
├─ app/                    # FastAPI application with Dockerfile and /healthz route
├─ deploy/cdk/             # CDK app and stacks
│  ├─ app.py               # CDK entry point
│  ├─ cdk.json             # Default context values
│  └─ stacks/              # Network, service, observability, deployment constructs
├─ .github/workflows/      # GitHub Actions pipeline for CDK deploys
├─ Makefile                # One-command UX for bootstrapping and deploying
└─ README.md               # This file
```

## Features

### Production-Grade Architecture
- Multi-AZ VPC deployment across 3 availability zones
- Auto-scaling based on CPU and request count metrics
- Health checks and automatic task replacement
- Flow logs for network traffic visibility

### Security & Compliance
- GitHub Actions OIDC integration (no long-lived AWS credentials)
- IAM permissions boundary for least-privilege access
- Secrets stored in AWS Secrets Manager
- Private subnets for compute resources
- Security groups with minimal required access

### Observability
- CloudWatch Logs with 30-day retention
- Custom CloudWatch dashboard for CPU and request metrics
- VPC Flow Logs for network audit trail
- Optional ADOT collector for distributed tracing

### Deployment Strategy
- Infrastructure as Code with AWS CDK
- Automated CI/CD via GitHub Actions
- Optional blue/green deployments with CodeDeploy
- Canary deployment support (10% traffic, 5-minute wait)

## Prerequisites

* Python 3.11
* Node.js 18+ (for the CDK CLI)
* AWS CLI v2 configured with credentials capable of bootstrapping the target account
* Docker (for building the container image asset)
* AWS CDK CLI (`npm install -g aws-cdk`)

## Bootstrapping

1. Install the Python dependencies:
   ```bash
   pip install -r deploy/cdk/requirements.txt
   ```
2. Bootstrap the target AWS account/region:
   ```bash
   cd deploy/cdk
   cdk bootstrap
   ```

## Configuration

Update `deploy/cdk/cdk.json` or pass `--context` values during `cdk deploy` to customise:

* `serviceName` – logical name for the stack and ECS service
* `minTaskCount` / `maxTaskCount` – autoscaling boundaries
* `cpuTargetUtilizationPercent` – CPU target for scaling
* `enableCodeDeploy` – set to `true` to enable CodeDeploy blue/green deployments
* `enableAdot` – set to `true` to add the ADOT collector sidecar
* `githubOrg` / `githubRepo` – used to scope the GitHub Actions OIDC trust policy

Secrets are managed through AWS Secrets Manager (see `AppSecret` in the CDK stack) and parameters through Systems Manager Parameter Store.

## One-command deploy

Run the make target to build the container image, bootstrap the environment, and deploy:

```bash
make deploy
```

The command outputs the Application Load Balancer DNS name when finished. The service exposes `/` and `/healthz` endpoints over HTTP port 80.

## GitHub Actions pipeline

`.github/workflows/deploy.yml` configures a deployment workflow that:

1. Assumes the CDK deploy role using GitHub Actions OIDC (no long-lived AWS keys).
2. Sets up Node.js and installs CDK CLI.
3. Sets up Python and installs CDK dependencies.
4. Runs `cdk diff` for visibility and `cdk deploy` with `--require-approval never`.

The workflow triggers automatically on pushes to the `main` branch and can also be manually triggered via `workflow_dispatch`.

Populate the following GitHub repository secrets/variables before running the workflow:

* Secrets
  * `AWS_ACCOUNT_ID` - Your AWS account ID
  * `AWS_REGION` - AWS region for deployment (e.g., `us-east-1`)
  * `AWS_DEPLOY_ROLE_ARN` - IAM role ARN output from the CDK stack deployment
* Variables
  * `GITHUB_ORG` - GitHub organization name (e.g., `ArmanShirzad`)
  * `GITHUB_REPO` - GitHub repository name (e.g., `aws-fargate-cdk-Production-infrastructure`)

## Blue/Green & canary deployments

When `enableCodeDeploy` is `true`, the stack provisions an ECS CodeDeploy application with a 10% → 100% canary rollout and a dedicated test listener. You can also perform manual canaries by adjusting the weights on the provisioned target groups.

## Observability

CloudWatch Logs capture application and optional ADOT sidecar output. A CloudWatch dashboard tracks CPU utilisation and ALB request counts. 

**Note**: Enabling ADOT (`enableAdot: true`) requires additional configuration. The ADOT collector references `/etc/aws-otel-config.yaml` which must be provided via a Docker volume or similar mechanism.

### Metrics Tracked
- CPU utilization across all tasks
- Request count per target group
- Health check status
- Network flow logs (VPC level)

## Cleanup

Destroy the stack and associated resources:

```bash
cd deploy/cdk
cdk destroy
```

## Project Status

This project demonstrates production-ready AWS infrastructure using Infrastructure as Code (IaC) principles. The codebase follows industry best practices for:

- **Reliability**: Multi-AZ deployment, auto-scaling, health checks
- **Security**: IAM least privilege, OIDC authentication, secrets management
- **Observability**: Comprehensive logging and monitoring
- **Maintainability**: Infrastructure as Code with CDK
- **DevOps**: Automated CI/CD with GitHub Actions

## License

This project is provided as-is for educational and demonstration purposes.

