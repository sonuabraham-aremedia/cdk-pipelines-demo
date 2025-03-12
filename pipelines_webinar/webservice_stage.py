import aws_cdk as cdk
from constructs import Construct
from .pipelines_webinar_stack import PipelinesWebinarStack

class WebServiceStage(cdk.Stage):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        service = PipelinesWebinarStack(self, "WebService")

        self.url_output = service.url_output
