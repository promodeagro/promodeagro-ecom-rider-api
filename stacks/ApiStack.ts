import { UserPool, UserPoolClient } from "aws-cdk-lib/aws-cognito";
import * as dynamodb from "aws-cdk-lib/aws-dynamodb";
import * as iam from "aws-cdk-lib/aws-iam";
import * as dotenv from 'dotenv';
import { Api, Bucket, Cognito, StackContext, Table } from "sst/constructs";
dotenv.config();


export function API({ app, stack }: StackContext) {

  const isProd = app.stage == "prod"

  const userPool = isProd ? process.env.COGNITO_USER_POOL_PROD : process.env.COGNITO_USER_POOL_DEV
  const clientPool = isProd ? process.env.COGNITO_CLIENT_POOL_PROD : process.env.COGNITO_CLIENT_POOL_DEV

  const cognito = new Cognito(stack, "Auth", {
    cdk: {
      userPool: UserPool.fromUserPoolId(stack, "UserPool", userPool!),
      userPoolClient: UserPoolClient.fromUserPoolClientId(
        stack,
        "UserPoolClient",
        clientPool!
      ),
    },
  })

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
  })

  const usersTable = new Table(
    stack,
    "usersTable", {
    cdk: { table: dynamodb.Table.fromTableArn(stack, "USERS_TABLE", isProd ? "arn:aws:dynamodb:ap-south-1:851725323791:table/prod-promodeagro-admin-promodeagroUsers" : "arn:aws:dynamodb:ap-south-1:851725323791:table/dev-promodeagro-admin-promodeagroUsers") }
  })

  const api = new Api(stack, "api", {
    authorizers: {
      UserPoolAuthorizer: {
        type: "user_pool",
        userPool: {
          id: cognito.userPoolId,
          clientIds: [cognito.userPoolClientId],
        },
      },
    },
    defaults: {
      authorizer: "UserPoolAuthorizer",
      function: {
        bind: [ridersTable, packerTable, runsheetTable, ordersTable, usersTable],
      }
    },
    routes: {
      "POST /auth/signin": {
        authorizer: "none",
        function: {
          handler: "packages/functions/api/auth/auth.signinHandler",
          environment: {
            USER_POOL_ID: cognito.userPoolId,
            COGNITO_CLIENT: cognito.userPoolClientId,
          },
          permissions: [
            "cognito-idp:AdminCreateUser",
            "cognito-idp:AdminConfirmSignUp",
            "cognito-idp:AdminUpdateUserAttributes",
            "cognito-idp:AdminSetUserPassword",
            "cognito-idp:AdminInitiateAuth"
          ],

        }
      },
      "POST /auth/validate-otp": {
        authorizer: "none",
        function: {
          handler: "packages/functions/api/auth/auth.validateOtpHandler",
          environment: {
            USER_POOL_ID: cognito.userPoolId,
            COGNITO_CLIENT: cognito.userPoolClientId,
          },
          permissions: [
            "cognito-idp:AdminCreateUser",
            "cognito-idp:AdminConfirmSignUp",
            "cognito-idp:AdminUpdateUserAttributes",
            "cognito-idp:AdminSetUserPassword",
            "cognito-idp:AdminInitiateAuth"
          ],
        }
      },
      "POST /auth/refresh-token": {
        authorizer: "none",
        function: {
          handler: "packages/functions/api/auth/auth.refreshAccessTokenHandler",
          environment: {
            USER_POOL_ID: cognito.userPoolId,
            COGNITO_CLIENT: cognito.userPoolClientId,
          },
          permissions: [
            "cognito-idp:AdminInitiateAuth"
          ],


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
      UserPoolAuthorizer: {
        type: "user_pool",
        userPool: {
          id: cognito.userPoolId,
          clientIds: [cognito.userPoolClientId],
        },
      },
    },
    defaults: {
      authorizer: "UserPoolAuthorizer",
      //   function: {
      //     bind: [packerTable, ordersTable],
      //   }
    },
    routes: {
      "POST /auth/signin": {
        authorizer: "none",
        function: {
          handler: "packages/functions/api/auth/auth.signin",
        }
      },
      "POST /auth/validate-otp": {
        authorizer: "none",
        function: {
          handler: "packages/functions/api/auth/auth.validateOtpHandler",
        }
      },
      "POST /auth/refresh-token": {
        authorizer: "none",
        function: {
          handler: "packages/functions/api/auth/auth.refreshAccessTokenHandler",
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
  });
}
