import { z } from "zod";
import middy from "@middy/core";
import { bodyValidator } from "../util/bodyValidator";
import { errorHandler } from "../util/errorHandler";
import { listOrders, packOrder } from ".";

export const listOrdersHandler = middy(async (event) => {
	let id = event.pathParameters.id;
	if (!id) {
		return {
			status: 400,
			body: JSON.stringify({
				message: "invalid id",
			}),
		};
	}
	return await listOrders(id);
}).use(errorHandler());

const patchOrderSchema = z.object({
	action: z.enum(["pack"]),
	image: z.string().url(),
});

export const packOrderHandler = middy(async (event) => {
	let id = event.pathParameters.id;
	if (!id) {
		return {
			status: 400,
			body: JSON.stringify({
				message: "invalid id",
			}),
		};
	}
	const { action, image } = JSON.parse(event.body);
	if (action === "pack") {
		return await packOrder(id, image);
	}
})
	.use(bodyValidator(patchOrderSchema))
	.use(errorHandler());
