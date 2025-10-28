"""Observability constructs for logs, metrics, and tracing."""

from aws_cdk import Duration
from aws_cdk import aws_cloudwatch as cloudwatch
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_elasticloadbalancingv2 as elbv2
from aws_cdk import aws_logs as logs
from constructs import Construct


class Observability(Construct):
    """Attach log groups, dashboards, and optional ADOT collector."""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        service: ecs.FargateService,
        target_group: elbv2.IApplicationTargetGroup,
        log_group: logs.ILogGroup,
        enable_adot: bool = False,
    ) -> None:
        super().__init__(scope, construct_id)

        # Basic dashboard tracking service metrics.
        dashboard = cloudwatch.Dashboard(self, "ServiceDashboard")
        dashboard.add_widgets(
            cloudwatch.GraphWidget(
                title="Service CPU Utilization",
                left=[
                    service.metric_cpu_utilization(period=Duration.minutes(1)),
                ],
            ),
            cloudwatch.GraphWidget(
                title="ALB Request Count",
                left=[
                    target_group.metric_request_count(period=Duration.minutes(1)),
                ],
            ),
        )

        if enable_adot:
            # Add ADOT collector as sidecar for traces/metrics.
            collector_container = service.task_definition.add_container(
                "AdotCollector",
                image=ecs.ContainerImage.from_registry("amazon/aws-otel-collector:latest"),
                essential=False,
                command=[
                    "--config",
                    "/etc/aws-otel-config.yaml",
                ],
                logging=ecs.LogDrivers.aws_logs(stream_prefix="adot", log_group=log_group),
            )
            collector_container.add_port_mappings(ecs.PortMapping(container_port=4317, protocol=ecs.Protocol.TCP))

