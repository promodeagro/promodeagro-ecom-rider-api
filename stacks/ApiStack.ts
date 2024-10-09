import { StackContext, Api, Table } from "sst/constructs";

export function API({ stack }: StackContext) {

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
      primaryIndex: { partitionKey: "id", sortKey: "createdAt" },
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
      "POST /": "packages/functions/api/auth.signin"
    },
  });


  stack.addOutputs({
    ApiEndpoint: api.url,
  });
}
