#!/usr/bin/env python3
"""Entry point for the AWS CDK application."""

import aws_cdk as cdk

from stacks.service_stack import ServiceStack


app = cdk.App()

service_name = app.node.try_get_context("serviceName") or "audi-fargate"
enable_code_deploy = (app.node.try_get_context("enableCodeDeploy") or "false").lower() == "true"
enable_adot = (app.node.try_get_context("enableAdot") or "false").lower() == "true"
min_task_count = int(app.node.try_get_context("minTaskCount") or 1)
max_task_count = int(app.node.try_get_context("maxTaskCount") or 5)
cpu_target = int(app.node.try_get_context("cpuTargetUtilizationPercent") or 55)
github_org = app.node.try_get_context("githubOrg") or "your-org"
github_repo = app.node.try_get_context("githubRepo") or "your-repo"

ServiceStack(
    app,
    f"{service_name}-stack",
    service_name=service_name,
    enable_code_deploy=enable_code_deploy,
    enable_adot=enable_adot,
    min_task_count=min_task_count,
    max_task_count=max_task_count,
    cpu_target_utilization_percent=cpu_target,
    github_org=github_org,
    github_repo=github_repo,
)

app.synth()

