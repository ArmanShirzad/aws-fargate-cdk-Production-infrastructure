"""Top-level stack wiring the network, service, deployments, and observability."""

from aws_cdk import CfnOutput
from aws_cdk import Stack
from aws_cdk import aws_iam as iam
from constructs import Construct

from .alb_fargate import FargateService
from .deployments import BlueGreenDeployment
from .network import Network
from .observability import Observability


class ServiceStack(Stack):
    """Stack that provisions the full service footprint."""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        service_name: str,
        enable_code_deploy: bool,
        enable_adot: bool,
        min_task_count: int,
        max_task_count: int,
        cpu_target_utilization_percent: int,
        github_org: str,
        github_repo: str,
    ) -> None:
        super().__init__(scope, construct_id)

        network = Network(self, "Network", max_azs=3)

        service = FargateService(
            self,
            "Service",
            vpc=network.vpc,
            service_name=service_name,
            min_task_count=min_task_count,
            max_task_count=max_task_count,
            cpu_target_utilization_percent=cpu_target_utilization_percent,
            enable_code_deploy=enable_code_deploy,
        )

        Observability(
            self,
            "Observability",
            service=service.service,
            target_group=service.alb_service.target_group,
            log_group=service.log_group,
            enable_adot=enable_adot,
        )

        if enable_code_deploy:
            BlueGreenDeployment(
                self,
                "BlueGreen",
                service=service.service,
                production_listener=service.production_listener,
                test_listener=service.canary_listener,
                prod_target_group=service.alb_service.target_group,
                test_target_group=service.canary_target_group,
            )

        boundary = iam.ManagedPolicy(
            self,
            "PermissionsBoundary",
            managed_policy_name=f"{service_name}-deployment-boundary",
            statements=[
                iam.PolicyStatement(
                    actions=[
                        "cloudformation:*",
                        "ecs:*",
                        "ec2:Describe*",
                        "ec2:CreateTags",
                        "ec2:DeleteTags",
                        "iam:PassRole",
                        "logs:*",
                        "elasticloadbalancing:*",
                        "codedeploy:*",
                        "ssm:*",
                        "secretsmanager:*",
                    ],
                    resources=["*"],
                )
            ],
        )

        deploy_role = iam.Role(
            self,
            "CiDeployRole",
            assumed_by=iam.WebIdentityPrincipal(
                "token.actions.githubusercontent.com",
                conditions={
                    "StringEquals": {
                        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
                    },
                    "StringLike": {
                        "token.actions.githubusercontent.com:sub": f"repo:{github_org}/{github_repo}:*",
                    },
                },
            ),
            description="Role assumed by GitHub Actions via OIDC for CDK deploys.",
            permissions_boundary=boundary,
        )

        deploy_role.add_to_principal_policy(
            iam.PolicyStatement(
                actions=[
                    "sts:AssumeRole",
                    "cloudformation:*",
                    "ecs:*",
                    "ec2:Describe*",
                    "ec2:CreateTags",
                    "ec2:DeleteTags",
                    "iam:PassRole",
                    "logs:*",
                    "elasticloadbalancing:*",
                    "codedeploy:*",
                    "ssm:*",
                    "secretsmanager:*",
                ],
                resources=["*"],
            )
        )

        CfnOutput(self, "LoadBalancerDNS", value=service.load_balancer.load_balancer_dns_name)
        CfnOutput(self, "DeployRoleArn", value=deploy_role.role_arn)

