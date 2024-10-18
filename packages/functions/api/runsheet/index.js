import { Table } from "sst/node/table";
import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import {
	DynamoDBDocumentClient,
	PutCommand,
	ScanCommand,
	GetCommand,
	UpdateCommand,
	QueryCommand,
	BatchGetCommand,
} from "@aws-sdk/lib-dynamodb";
import { save, update, findById } from "../common/db";
import crypto from "crypto";

const client = new DynamoDBClient({ region: "ap-south-1" });
const docClient = DynamoDBDocumentClient.from(client);

const riderTable = Table.ridersTable.tableName;
const runsheetTable = Table.runsheetTable.tableName;
const ordersTable = Table.ordersTable.tableName;

export const listRunsheets = async (id) => {
	const params = {
		TableName: runsheetTable,
		IndexName: "riderIndex",
		KeyConditionExpression: "#riderId = :riderId",
		FilterExpression: "#status IN (:pending, :active)",
		ExpressionAttributeNames: {
			"#riderId": "riderId",
			"#status": "status",
		},
		ExpressionAttributeValues: {
			":riderId": id,
			":pending": "pending",
			":active": "active",
		},
	};
	const data = await docClient.send(new QueryCommand(params));
	const allOrders = data.Items.flatMap((item) => item.orders);
	const orderStatuses = await getOrderStatuses(allOrders);

	return data.Items.map((item) => {
		const totalOrders = item.orders.length;
		const itemOrderStatuses = item.orders.map(
			(orderId) => orderStatuses[orderId]
		);
		const pendingOrders = itemOrderStatuses.filter(
			(status) => status !== "delivered"
		).length;
		const deliveredOrders = totalOrders - pendingOrders;

		return {
			id: item.id,
			orders: totalOrders,
			pendingOrders,
			deliveredOrders,
			amountCollectable: item.amountCollectable,
		};
	});
};

const getOrderStatuses = async (orderIds) => {
	if (orderIds.length === 0) return {};

	const params = {
		RequestItems: {
			[ordersTable]: {
				Keys: orderIds.map((id) => ({ id })),
				ProjectionExpression: "id, #status",
				ExpressionAttributeNames: { "#status": "status" },
			},
		},
	};

	const result = await docClient.send(new BatchGetCommand(params));
	return Object.fromEntries(
		result.Responses[ordersTable].map((item) => [item.id, item.status])
	);
};

export const acceptRunsheet = async (runsheetId) => {
	return await update(
		runsheetTable,
		{
			id: runsheetId,
		},
		{
			status: "active",
			acceptedAt: new Date().toISOString(),
		}
	);
};

export const getRunsheet = async (id) => {
	const runsheet = await findById(runsheetTable, id);
	const ordersParam = {
		RequestItems: {
			[ordersTable]: {
				Keys: runsheet.orders.map((id) => ({ id })),
			},
		},
	};
	const response = await docClient.send(new BatchGetCommand(ordersParam));
	const orders = response.Responses[ordersTable].map((order) => {
		delete order._version;
		delete order.taskToken;
		delete order.__typename;
		return order;
	});
	runsheet.orders = orders;
	return runsheet;
};

export const confirmOrder = async (runsheetId, orderId, image) => {
	const runsheet = await findById(runsheetTable, runsheetId);
	const exists = runsheet.orders.includes(orderId);
	if (!exists) {
		return {
			statusCode: 400,
			body: JSON.stringify({
				message: "order doesnt exist in runsheet.",
			}),
		};
	}
	const order = await findById(ordersTable, orderId);
	order.paymentDetails.status = "DONE";
	return await update(
		ordersTable,
		{
			id: orderId,
		},
		{
			status: "delivered",
			deliveredAt: new Date().toISOString(),
			deliveredImage: image,
			paymentDetails: order.paymentDetails,
		}
	);
};

export const cancelOrder = async (runsheetId, orderId, reason) => {
	const runsheet = await findById(runsheetTable, runsheetId);
	const exists = runsheet.orders.includes(orderId);
	if (!exists) {
		return {
			statusCode: 400,
			body: JSON.stringify({
				message: "order doesnt exist in runsheet.",
			}),
		};
	}
	const cancellationData = {
		status: "cancelled",
		cancelledAt: new Date().toISOString(),
		cancelReason: reason,
		cancellationBy: "rider",
	};
	return await update(
		ordersTable,
		{
			id: orderId,
		},
		{
			status: "cancelled",
			cancellationData: cancellationData,
		}
	);
};
