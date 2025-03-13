import { SecretValue, Stack, StackProps } from "aws-cdk-lib";
import { Construct } from "constructs";
import * as codepipeline from "aws-cdk-lib/aws-codepipeline";
import * as codepipelineActions from "aws-cdk-lib/aws-codepipeline-actions";
import * as pipelines from "aws-cdk-lib/pipelines";
import { WebServiceStage } from "./webservice_stage";
import { CodeBuildStep } from "aws-cdk-lib/pipelines";

export class PipelineStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const sourceArtifact = new codepipeline.Artifact();
    const cloudAssemblyArtifact = new codepipeline.Artifact();

    const sourceAction = new codepipelineActions.GitHubSourceAction({
      actionName: "GitHub",
      output: sourceArtifact,
      oauthToken: SecretValue.secretsManager("github-token"),
      owner: "sonuabraham-aremedia",
      repo: "cdk-pipelines-demo",
      branch: "typescript",
      trigger: codepipelineActions.GitHubTrigger.POLL,
    });

    const synthAction = new CodeBuildStep("Synth", {
      input: pipelines.CodePipelineSource.gitHub(
        "sonuabraham-aremedia/cdk-pipelines-demo",
        "typescript",
        {
          authentication: SecretValue.secretsManager("github-oauth-token1"),
        }
      ),
      installCommands: ["npm install"],
      commands: ["npm run build", "npm test"], // Correctly using commands property
      primaryOutputDirectory: "cdk.out",
    });
    const pipeline = new pipelines.CodePipeline(this, "Pipeline", {
      synth: synthAction,
    });

    // Pre-prod
    const preProdApp = new WebServiceStage(this, "Pre-Prod");
    const preProdStage = pipeline.addStage(preProdApp);
    const serviceUrl = preProdApp.urlOutput;

    preProdStage.addPost(
      new pipelines.ShellStep("IntegrationTests", {
        commands: ["npm install", "npm run build", "npm run integration"],
        envFromCfnOutputs: {
          SERVICE_URL: serviceUrl,
        },
      })
    );

    // Prod
    const prodApp = new WebServiceStage(this, "Prod");
    pipeline.addStage(prodApp);
  }
}
