"""Deployment utilities for blue/green and canary releases."""

from aws_cdk import Duration
from aws_cdk import aws_codedeploy as codedeploy
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_elasticloadbalancingv2 as elbv2
from aws_cdk import aws_iam as iam
from constructs import Construct


class BlueGreenDeployment(Construct):
    """Configure CodeDeploy blue/green for an ECS service."""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        service: ecs.FargateService,
        production_listener: elbv2.IApplicationListener,
        test_listener: elbv2.IApplicationListener,
        prod_target_group: elbv2.IApplicationTargetGroup,
        test_target_group: elbv2.IApplicationTargetGroup,
    ) -> None:
        super().__init__(scope, construct_id)

        application = codedeploy.EcsApplication(
            self,
            "CodeDeployApplication",
            application_name=f"{service.cluster.cluster_name}-{service.service_name}",
        )

        role = iam.Role(
            self,
            "CodeDeployRole",
            assumed_by=iam.ServicePrincipal("codedeploy.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AWSCodeDeployRoleForECS"),
            ],
        )

        self.deployment_group = codedeploy.EcsDeploymentGroup(
            self,
            "DeploymentGroup",
            service=service,
            application=application,
            role=role,
            deployment_config=codedeploy.EcsDeploymentConfig.CANARY_10PERCENT_5MINUTES,
            blue_green_deployment_config=codedeploy.EcsBlueGreenDeploymentConfig(
                blue_target_group=prod_target_group,
                green_target_group=test_target_group,
                listener=production_listener,
                test_listener=test_listener,
                termination_wait_time=Duration.minutes(5),
            ),
        )

