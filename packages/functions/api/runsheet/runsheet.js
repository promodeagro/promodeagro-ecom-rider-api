import { z } from "zod";
import middy from "@middy/core";
import { bodyValidator } from "../util/bodyValidator";
import { errorHandler } from "../util/errorHandler";
import {
	listRunsheets,
	acceptRunsheet,
	getRunsheet,
	confirmOrder,
	cancelOrder,
} from ".";

//TODO: compare riderid with id from jwt token

export const listRunsheetsHandler = middy(async (event) => {
	let id = event.pathParameters.id;
	if (!id) {
		return {
			status: 400,
			body: JSON.stringify({
				message: "invalid id",
			}),
		};
	}
	return await listRunsheets(id);
}).use(errorHandler());

export const acceptRunsheetHandler = middy(async (event) => {
	let id = event.pathParameters.id;
	let runsheetId = event.pathParameters.runsheetId;
	if (!id || !runsheetId) {
		return {
			status: 400,
			body: JSON.stringify({
				message: "invalid id",
			}),
		};
	}
	return await acceptRunsheet(runsheetId);
}).use(errorHandler());

export const getRunsheetHandler = middy(async (event) => {
	let id = event.pathParameters.id;
	let runsheetId = event.pathParameters.runsheetId;
	if (!id || !runsheetId) {
		return {
			status: 400,
			body: JSON.stringify({
				message: "invalid id",
			}),
		};
	}
	return await getRunsheet(runsheetId);
}).use(errorHandler());

const imageSchema = z.object({
	image: z.string().url({
		message: "delivered image is required to complete the delivery",
	}),
});

export const confirmOrderHandler = middy(async (event) => {
	let id = event.pathParameters.id;
	let runsheetId = event.pathParameters.runsheetId;
	let orderId = event.pathParameters.orderId;
	const { image } = JSON.parse(event.body);
	if (!id || !runsheetId) {
		return {
			status: 400,
			body: JSON.stringify({
				message: "invalid id",
			}),
		};
	}
	return await confirmOrder(runsheetId, orderId, image);
})
	.use(bodyValidator(imageSchema))
	.use(errorHandler());

const reasonSchema = z.object({
	reason: z.string({
		message: "reason required for cancellation",
	}),
});
export const cancelOrderHandler = middy(async (event) => {
	let id = event.pathParameters.id;
	let runsheetId = event.pathParameters.runsheetId;
	let orderId = event.pathParameters.orderId;
	const { reason } = JSON.parse(event.body);
	if (!id || !runsheetId) {
		return {
			status: 400,
			body: JSON.stringify({
				message: "invalid id",
			}),
		};
	}
	return await cancelOrder(runsheetId, orderId, reason);
})
	.use(bodyValidator(reasonSchema))
	.use(errorHandler());
