import { Table } from "sst/node/table";
import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import {
	DynamoDBDocumentClient,
	PutCommand,
	ScanCommand,
	GetCommand,
	UpdateCommand,
	QueryCommand,
} from "@aws-sdk/lib-dynamodb";
import { save, update } from "../common/db";

const client = new DynamoDBClient({ region: "ap-south-1" });
const docClient = DynamoDBDocumentClient.from(client);

const riderTable = Table.ridersTable.tableName;

export const numberExists = async (number) => {
	const params = {
		TableName: riderTable,
		IndexName: "numberIndex",
		KeyConditionExpression: "#number = :number",
		ExpressionAttributeNames: {
			"#number": "number",
		},
		ExpressionAttributeValues: {
			":number": number,
		},
	};
	const command = new QueryCommand(params);
	const res = await docClient.send(command);
	return res.Items;
};

export const saveOtp = async (id, otp) => {
	await update(
		riderTable,
		{
			id: id,
		},
		{
			otp: otp,
			otpExpire: Math.floor(Date.now() / 1000) + 180,
			updatedAt: new Date().toISOString(),
		}
	);
};
