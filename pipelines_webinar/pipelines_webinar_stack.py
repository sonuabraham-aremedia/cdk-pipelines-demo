import os
from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as lmb,
    aws_apigateway as apigw,
    aws_cloudwatch as cloudwatch,
    aws_codedeploy as codedeploy,
    CfnOutput
)
from constructs import Construct

class PipelinesWebinarStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # The code that defines your stack goes here
        this_dir = os.path.dirname(__file__)

        handler = lmb.Function(self, 'Handler',
            runtime=lmb.Runtime.PYTHON_3_9,  # Updated to a supported version
            handler='handler.handler',
            code=lmb.Code.from_asset(os.path.join(this_dir, 'lambda')))

        alias = lmb.Alias(self, 'HandlerAlias',
            alias_name='Current',
            version=handler.current_version)

        gw = apigw.LambdaRestApi(self, 'Gateway',
            description='Endpoint for a simple Lambda-powered web service',
            handler=alias)

        failure_alarm = cloudwatch.Alarm(self, 'FailureAlarm',
            metric=cloudwatch.Metric(
                metric_name='5XXError',
                namespace='AWS/ApiGateway',
                dimensions_map={
                    'ApiName': 'Gateway',
                },
                statistic='Sum',
                period=Duration.minutes(1)),
            threshold=1,
            evaluation_periods=1)

        codedeploy.LambdaDeploymentGroup(self, 'DeploymentGroup',
            alias=alias,
            deployment_config=codedeploy.LambdaDeploymentConfig.CANARY_10_PERCENT_10_MINUTES,
            alarms=[failure_alarm])

        self.url_output = CfnOutput(self, 'Url',
            value=gw.url)
