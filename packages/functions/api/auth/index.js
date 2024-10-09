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
import { save } from "../common/db";

const client = new DynamoDBClient({ region: "ap-south-1" });
const docClient = DynamoDBDocumentClient.from(client);

const riderTable = Table.riderTable.tableName;

export const numberExists = async (number) => {
	const params = {
		TableName: riderTable,
		IndexName: "numberIndex",
		KeyConditionExpression: "#number = :number",
		ExpressionAttributesNames: {
			":number": "number",
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
		}
	);
};

export const createRider = async (number, otp) => {
	const id = crypto.randomUUID();
	const rider = {
		id: id,
		number: number,
		otp: otp,
		otpExpire: Math.floor(Date.now() / 1000) + 180,
		profileStatus: JSON.stringify({
			personalInfoCompleted: false,
			bankDetailsCompleted: false,
			addressCompleted: false,
			otherDetailsCompleted: false,
		}),
		personalDetails: "{}",
		bankDetails: "{}",
		documents: "{}",
		accountVerified: false,
	};
	return await save(riderTable, rider);
};
