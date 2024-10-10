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

export const validateOtp = async (otp, number) => {
	const params = {
		TableName: riderTable,
		IndexName: "numberIndex",
		KeyConditionExpression: "#num = :num",
		ExpressionAttributeNames: {
			"#num": "number",
		},
		ExpressionAttributeValues: {
			":num": number,
		},
		Limit: 1,
	};
	const result = await docClient.send(new QueryCommand(params));
	if (result.Items || result.Items.length === 0) {
		return {
			statusCode: 404,
			message: JSON.stringify({
				message: "Number not found",
			}),
		};
	}
	const resOtp = result.Items[0].otp;
	const expired = result.Items[0].otpExpire;
	if (Math.floor(Date.now() / 1000) > expired) {
		return {
			statusCode: 400,
			message: JSON.stringify({
				message: "otp expired",
			}),
		};
	}
	if (resOtp === otp) {
		//TODO - return jwt tokens
		return {
			statusCode: 200,
			message: JSON.stringify({
				message: "authenticated successfully",
			}),
		};
	}
	return {
		statusCode: 401,
		message: JSON.stringify({
			message: "Invalid OTP",
		}),
	};
};
