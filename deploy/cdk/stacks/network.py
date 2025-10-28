"""Networking constructs for the service."""

from aws_cdk import Duration
from aws_cdk import aws_ec2 as ec2
from constructs import Construct


class Network(Construct):
    """Provision a multi-AZ VPC with public and private subnets."""

    def __init__(self, scope: Construct, construct_id: str, *, max_azs: int = 2) -> None:
        super().__init__(scope, construct_id)

        self.vpc = ec2.Vpc(
            self,
            "Vpc",
            max_azs=max_azs,
            nat_gateways=1,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24,
                ),
                ec2.SubnetConfiguration(
                    name="Private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24,
                ),
            ],
        )

        # Flow logs provide additional visibility into network traffic.
        ec2.FlowLog(
            self,
            "VpcFlowLogs",
            resource_type=ec2.FlowLogResourceType.from_vpc(self.vpc),
            traffic_type=ec2.FlowLogTrafficType.ALL,
            max_aggregation_interval=Duration.minutes(5),
        )

