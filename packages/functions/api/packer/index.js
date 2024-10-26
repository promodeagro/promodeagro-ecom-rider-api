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

const ordersTable = Table.ordersTable.tableName;

export const listOrders = async () => {
	const params = {
		TableName: ordersTable,
		IndexName: "statusCreatedAtIndex",
		ScanIndexForward: true,
		KeyConditionExpression: `#s = :status`,
		ProjectionExpression:
			"#totalPrice, #paymentDetails, #tax, #createdAt, #totalSavings, #items, #deliveryCharges, #subTotal, #deliverySlot, #id",
		ExpressionAttributeNames: {
			"#s": "status",
			"#totalPrice": "totalPrice",
			"#paymentDetails": "paymentDetails",
			"#tax": "tax",
			"#createdAt": "createdAt",
			"#totalSavings": "totalSavings",
			"#items": "items",
			"#deliveryCharges": "deliveryCharges",
			"#subTotal": "subTotal",
			"#deliverySlot": "deliverySlot",
			"#id": "id",
		},
		ExpressionAttributeValues: {
			":status": "order placed",
		},
		Limit: 100,
	};
	const res = await docClient.send(new QueryCommand(params));
	return res.Items;
};

export const packOrder = async (id, image) => {
	const order = await findById(ordersTable, id);
	if (!order) {
		return {
			statusCode: 400,
			body: JSON.stringify({
				message: "order doesnt exist.",
			}),
		};
	}
	if (order.status !== "order placed") {
		return {
			statusCode: 400,
			body: JSON.stringify({
				message: "order already packed.",
			}),
		};
	}
	const time = new Date().toISOString();
	await update(
		ordersTable,
		{
			id: id,
		},
		{
			status: "packed",
			packedImage: image,
			packedAt: time,
			updatedAt: time,
		}
	);
	return {
		statusCode: 200,
		body: JSON.stringify({
			message: "order packed",
		}),
	};
};
