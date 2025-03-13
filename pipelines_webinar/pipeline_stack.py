import aws_cdk as cdk
from aws_cdk import (
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as cpactions,
    pipelines
)
from constructs import Construct
from .webservice_stage import WebServiceStage

APP_ACCOUNT = '391970746680'

class PipelineStack(cdk.Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        source_artifact = codepipeline.Artifact()
        cloud_assembly_artifact = codepipeline.Artifact()

        pipeline = pipelines.CodePipeline(self, 'Pipeline',
            synth=pipelines.ShellStep(
                "Synth",
                input=pipelines.CodePipelineSource.git_hub(
                    "sonuabraham-aremedia/cdk-pipelines-demo",
                    "python",
                    authentication=cdk.SecretValue.secrets_manager("github-oauth-token1"),
                ),
                commands=[
                    "npm install -g aws-cdk",
                    "pip install -r requirements.txt",
                    "pytest unittests",
                    "cdk synth"
                ]
            )
        )

        pre_prod_app = WebServiceStage(self, "Pre-Prod", env={
            "account": APP_ACCOUNT,
            "region": "ap-southeast-2",
        })
        pre_prod_stage = pipeline.add_stage(pre_prod_app)
        pre_prod_stage.add_post(
            pipelines.ShellStep(
                "Integ",
                commands=[
                    "pip install -r requirements.txt",
                    "pytest integtests",
                ],
                env_from_cfn_outputs={
                    "SERVICE_URL": pre_prod_app.url_output
                }
            )
        )

        pipeline.add_stage(WebServiceStage(self, "Prod", env={
            "account": APP_ACCOUNT,
            "region": "ap-southeast-2",
        }))
