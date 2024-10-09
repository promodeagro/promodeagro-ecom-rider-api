import { SSTConfig } from "sst";
import { API } from "./stacks/ApiStack";

export default {
  config(_input) {
    return {
      name: "promodeagro-rider",
      region: "ap-south-1",
    };
  },
  stacks(app) {
    if (app.stage !== "prod") {
      app.setDefaultRemovalPolicy("destroy");
    }
    app.stack(API);
  }
} satisfies SSTConfig;
