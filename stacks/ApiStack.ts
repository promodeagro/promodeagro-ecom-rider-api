import { StackContext, Api, Table, Config, Bucket } from "sst/constructs";
import * as iam from "aws-cdk-lib/aws-iam";

export function API({ app, stack }: StackContext) {

  const isProd = app.stage == "prod"

  const SMS_AUTH = new Config.Secret(stack, "SMS_AUTH");
  const SMS_AUTH_TOKEN = new Config.Secret(stack, "SMS_AUTH_TOKEN");

  const mediaBucket = new Bucket(stack, "mediaBucket", {
    name: isProd ? "promodeagro-rider-media-bucket" : "dev-promodeagro-rider-media-bucket",
    cors: [
      {
        allowedOrigins: ["*"],
        allowedHeaders: ["*"],
        allowedMethods: ["GET", "PUT", "POST"],
      },
    ],

  });


  const getObjectPolicy = new iam.PolicyStatement({
    actions: ["s3:GetObject"],
    effect: iam.Effect.ALLOW,
    resources: [`${mediaBucket.bucketArn}/*`],
    principals: [new iam.AnyPrincipal()],
  });

  mediaBucket.attachPermissions([
    getObjectPolicy
  ])

  const ridersTable = new Table(
    stack,
    "ridersTable",
    {
      fields: {
        id: "string",
        number: "string",
        otp: "string",
        createdAt: "string",
      },
      primaryIndex: { partitionKey: "id" },
      globalIndexes: {
        numberIndex: { partitionKey: "number" }
      }
    }
  );

  const tables = [ridersTable]
  const api = new Api(stack, "api", {
    defaults: {
      function: {
        bind: tables
      }
    },
    routes: {
      "POST /auth/signin": {
        function: {
          handler: "packages/functions/api/auth/auth.signin",
          bind: [SMS_AUTH, SMS_AUTH_TOKEN]
        }
      },
      "POST /auth/validate-otp": "packages/functions/api/auth/auth.validateOtpHandler",
      "PUT /rider/personal-details": "packages/functions/api/rider/update.updatePersonalDetails",
      "PUT /rider/bank-details": "packages/functions/api/rider/update.updatebankDetails",
      "PUT /rider/document-details": "packages/functions/api/rider/update.updateDocumentDetails",
      "PUT /rider/submit/{id}": "packages/functions/api/rider/update.submitRiderProfile",
      "GET /uploadUrl": {
        function: {
          handler:
            "packages/functions/api/media/getPreSignedS3url.handler",
          bind: [mediaBucket],
        },
      }
    },
  });


  stack.addOutputs({
    ApiEndpoint: api.url,
    sms_auth: SMS_AUTH.name,
    sms_auth_token: SMS_AUTH_TOKEN.name
  });
}
