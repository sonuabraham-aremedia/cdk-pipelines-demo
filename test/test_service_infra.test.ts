import { App } from "aws-cdk-lib";
import { Template } from "aws-cdk-lib/assertions";
import { PipelinesWebinarStack } from "../pipelines_webinar/pipelines_webinar_stack";

test("Lambda Handler", () => {
  // GIVEN
  const app = new App();

  // WHEN
  const stack = new PipelinesWebinarStack(app, "Stack");

  // Create a CloudFormation template from the synthesized stack
  const template = Template.fromStack(stack);

  // Find all AWS Lambda function resources in the template
  const functions = template.findResources("AWS::Lambda::Function");

  // THEN
  expect(Object.keys(functions).length).toEqual(1);
  const functionProperties = Object.values(functions)[0] as any;
  expect(functionProperties.Properties.Handler).toEqual("handler.handler");
});
