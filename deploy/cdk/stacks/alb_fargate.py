"""Application Load Balanced Fargate service construct."""

from pathlib import Path

from aws_cdk import Duration
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_ecs_patterns as ecs_patterns
from aws_cdk import aws_elasticloadbalancingv2 as elbv2
from aws_cdk import aws_iam as iam
from aws_cdk import aws_logs as logs
from aws_cdk import aws_secretsmanager as secretsmanager
from aws_cdk import aws_ssm as ssm
from constructs import Construct


class FargateService(Construct):
    """Provision an ECS Fargate service fronted by an Application Load Balancer."""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        vpc: ec2.IVpc,
        service_name: str,
        min_task_count: int,
        max_task_count: int,
        cpu_target_utilization_percent: int,
        enable_code_deploy: bool = False,
    ) -> None:
        super().__init__(scope, construct_id)

        self.log_group = logs.LogGroup(
            self,
            "ServiceLogGroup",
            log_group_name=f"/aws/ecs/{service_name}",
            retention=logs.RetentionDays.ONE_MONTH,
        )

        container_image_path = Path(__file__).resolve().parents[3] / "app"

        app_secret = secretsmanager.Secret(
            self,
            "AppSecret",
            secret_name=f"/{service_name}/app",
            description="Example secret injected into the Fargate task.",
        )

        self.alb_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            "FargateService",
            service_name=service_name,
            vpc=vpc,
            desired_count=min_task_count,
            assign_public_ip=False,
            cpu=512,
            memory_limit_mib=1024,
            health_check_grace_period=Duration.seconds(60),
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_asset(str(container_image_path)),
                container_port=8000,
                log_driver=ecs.LogDrivers.aws_logs(
                    stream_prefix="app",
                    log_group=self.log_group,
                ),
                environment={
                    "SERVICE_NAME": service_name,
                },
                secrets={
                    "APP_SECRET": ecs.Secret.from_secrets_manager(app_secret),
                },
            ),
            public_load_balancer=True,
            listener_port=80,
            deployment_controller=ecs.DeploymentController(
                type=ecs.DeploymentControllerType.CODE_DEPLOY
                if enable_code_deploy
                else ecs.DeploymentControllerType.ECS
            ),
        )

        self.alb_service.target_group.configure_health_check(path="/healthz")

        self.alb_service.task_definition.add_to_task_role_policy(
            iam.PolicyStatement(
                actions=[
                    "ssm:GetParameter",
                    "ssm:GetParameters",
                    "secretsmanager:GetSecretValue",
                ],
                resources=["*"],
            )
        )

        scaling = self.alb_service.service.auto_scale_task_count(
            min_capacity=min_task_count,
            max_capacity=max_task_count,
        )
        scaling.scale_on_cpu_utilization(
            "CpuScaling",
            target_utilization_percent=cpu_target_utilization_percent,
        )

        scaling.scale_on_request_count(
            "RequestScaling",
            requests_per_target=1000,
            target_group=self.alb_service.target_group,
        )

        self.production_listener = self.alb_service.listener
        self.load_balancer = self.alb_service.load_balancer
        self.service = self.alb_service.service
        self.task_definition = self.alb_service.task_definition

        self.canary_listener = self.load_balancer.add_listener(
            "CanaryListener",
            port=9001,
            protocol=elbv2.ApplicationProtocol.HTTP,
            open=False,
        )

        self.canary_target_group = elbv2.ApplicationTargetGroup(
            self,
            "CanaryTargetGroup",
            target_type=elbv2.TargetType.IP,
            port=8000,
            vpc=vpc,
            health_check=elbv2.HealthCheck(path="/healthz"),
        )
        self.canary_listener.add_target_groups("CanaryTargets", target_groups=[self.canary_target_group])
        self.service.attach_to_application_target_group(self.canary_target_group)

        ssm.StringParameter(
            self,
            "ExampleConfigParameter",
            parameter_name=f"/{service_name}/example-config",
            string_value="example",
        )

