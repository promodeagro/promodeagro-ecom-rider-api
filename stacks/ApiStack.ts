import { StackContext, Api, Table, Config, Bucket, Function } from "sst/constructs";
import * as iam from "aws-cdk-lib/aws-iam";
import * as dynamodb from "aws-cdk-lib/aws-dynamodb";


export function API({ app, stack }: StackContext) {

  const isProd = app.stage == "prod"

  const SMS_AUTH = new Config.Secret(stack, "SMS_AUTH");
  const SMS_AUTH_TOKEN = new Config.Secret(stack, "SMS_AUTH_TOKEN");
  const JWT_SECRET = new Config.Secret(stack, "JWT_SECRET");
  const JWT_REFRESH_SECRET = new Config.Secret(stack, "JWT_REFRESH_SECRET");

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

  const packerTable = new Table(
    stack,
    "packerTable",
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

  const runsheetTable = new Table(
    stack,
    "runsheetTable", {
    cdk: { table: dynamodb.Table.fromTableArn(stack, "RUNSHEET_TABLE", isProd ? "arn:aws:dynamodb:ap-south-1:851725323791:table/prod-promodeagro-admin-runsheetTable" : "arn:aws:dynamodb:ap-south-1:851725323791:table/dev-promodeagro-admin-runsheetTable") }
  }
  )
  const ordersTable = new Table(
    stack,
    "ordersTable", {
    cdk: { table: dynamodb.Table.fromTableArn(stack, "ORDER_TABLE", isProd ? "arn:aws:dynamodb:ap-south-1:851725323791:table/prod-promodeagro-admin-OrdersTable" : "arn:aws:dynamodb:ap-south-1:851725323791:table/dev-promodeagro-admin-OrdersTable") }
  }
  )

  const authorizerFun = new Function(stack, "Authorizer", {
    handler: "packages/functions/api/auth/auth.authorizerHandler",
    bind: [ridersTable, packerTable, JWT_SECRET, JWT_REFRESH_SECRET],
  })

  const api = new Api(stack, "api", {
    authorizers: {
      myAuthorizer: {
        type: "lambda",
        function: authorizerFun,
        resultsCacheTtl: "30 seconds",
      }
    },
    defaults: {
      authorizer: "myAuthorizer",
      function: {
        bind: [ridersTable, packerTable, runsheetTable, ordersTable],
      }
    },
    routes: {
      "POST /auth/signin": {
        authorizer: "none",
        function: {
          handler: "packages/functions/api/auth/auth.signin",
          bind: [SMS_AUTH, SMS_AUTH_TOKEN, JWT_SECRET, JWT_REFRESH_SECRET]
        }
      },
      "POST /auth/validate-otp": {
        authorizer: "none",
        function: {
          handler: "packages/functions/api/auth/auth.validateOtpHandler",
          bind: [JWT_SECRET, JWT_REFRESH_SECRET]
        }
      },
      "POST /auth/refresh-token": {
        authorizer: "none",
        function: {
          handler: "packages/functions/api/auth/auth.refreshAccessTokenHandler",
          bind: [JWT_SECRET, JWT_REFRESH_SECRET]
        }
      },
      "PUT /rider/personal-details": "packages/functions/api/rider/update.updatePersonalDetails",
      "PUT /rider/bank-details": "packages/functions/api/rider/update.updatebankDetails",
      "PUT /rider/document-details": "packages/functions/api/rider/update.updateDocumentDetails",
      "PUT /rider/submit/{id}": "packages/functions/api/rider/update.submitRiderProfile",
      "GET /rider/{id}/runsheet": "packages/functions/api/runsheet/runsheet.listRunsheetsHandler",
      "GET /rider/{id}/runsheet/{runsheetId}": "packages/functions/api/runsheet/runsheet.getRunsheetHandler",
      "GET /rider/{id}/runsheet/{runsheetId}/accept": "packages/functions/api/runsheet/runsheet.acceptRunsheetHandler",
      "PUT /rider/{id}/runsheet/{runsheetId}/order/{orderId}/complete": "packages/functions/api/runsheet/runsheet.confirmOrderHandler",
      "PUT /rider/{id}/runsheet/{runsheetId}/order/{orderId}/cancel": "packages/functions/api/runsheet/runsheet.cancelOrderHandler",
      "GET /packer/order": {
        authorizer: "none",
        function: {
          handler: "packages/functions/api/packer/packer.listOrdersHandler"
        }
      },
      "PATCH /packer/order/{id}": {
        authorizer: "none",
        function: {
          handler: "packages/functions/api/packer/packer.packOrderHandler"
        }
      },
      "GET /rider/uploadUrl": {
        function: {
          handler:
            "packages/functions/api/media/getPreSignedS3url.handler",
          bind: [mediaBucket],
        },
      }
    },
  });

  const packerApi = new Api(stack, "packerApi", {
    authorizers: {
      myAuthorizer: {
        type: "lambda",
        function: authorizerFun,
        resultsCacheTtl: "30 seconds",
      }
    },
    defaults: {
      authorizer: "myAuthorizer",
      function: {
        bind: [packerTable, ordersTable],
      }
    },
    routes: {
      "POST /auth/signin": {
        authorizer: "none",
        function: {
          handler: "packages/functions/api/auth/auth.signin",
          bind: [SMS_AUTH, SMS_AUTH_TOKEN, JWT_SECRET, JWT_REFRESH_SECRET]
        }
      },
      "POST /auth/validate-otp": {
        authorizer: "none",
        function: {
          handler: "packages/functions/api/auth/auth.validateOtpHandler",
          bind: [JWT_SECRET, JWT_REFRESH_SECRET]
        }
      },
      "POST /auth/refresh-token": {
        authorizer: "none",
        function: {
          handler: "packages/functions/api/auth/auth.refreshAccessTokenHandler",
          bind: [JWT_SECRET, JWT_REFRESH_SECRET]
        }
      },
      "GET /packer/order": {
        authorizer: "none",
        function: {
          handler: "packages/functions/api/packer/packer.listOrdersHandler"
        }
      },
      "PATCH /packer/order/{id}": {
        authorizer: "none",
        function: {
          handler: "packages/functions/api/packer/packer.packOrderHandler"
        }
      },
      "GET /packer/uploadUrl": {
        function: {
          handler:
            "packages/functions/api/media/getPreSignedS3url.handler",
          bind: [mediaBucket],
        },
      }
    },
  });


  stack.addOutputs({
    RiderEndpoint: api.url,
    PackerEndpoint: packerApi.url,
    sms_auth: SMS_AUTH.name,
    sms_auth_token: SMS_AUTH_TOKEN.name,
    jwt_secret: JWT_SECRET.name,
    jwt_refresh_secret: JWT_REFRESH_SECRET.name
  });
}
