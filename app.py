import aws_cdk as cdk
from pipelines_webinar.pipeline_stack import PipelineStack

PIPELINE_ACCOUNT = "391970746680"

app = cdk.App()
PipelineStack(app, "PipelineStack", env={
    "account": PIPELINE_ACCOUNT,
    "region": "ap-southeast-2",
})

app.synth()
