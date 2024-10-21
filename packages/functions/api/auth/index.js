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
import { generateTokens } from "./jwt";

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
		KeyConditionExpression: "#number = :number",
		ExpressionAttributeNames: {
			"#number": "number",
		},
		ExpressionAttributeValues: {
			":number": number,
		},
		Limit: 1,
	};
	const result = await docClient.send(new QueryCommand(params));
	if (!result.Items || result.Items.length === 0) {
		return {
			statusCode: 400,
			body: JSON.stringify({
				message: "Number not found",
			}),
		};
	}
	const resOtp = result.Items[0].otp;
	const expired = result.Items[0].otpExpire;
	if (resOtp == otp) {
		if (Math.floor(Date.now() / 1000) > expired) {
			return {
				statusCode: 401,
				body: JSON.stringify({
					message: "otp expired",
				}),
			};
		}
		const rider = result.Items[0];
		delete rider.otp;
		delete rider.otpExpire;
		const tokens = generateTokens({
			id: result.Items[0].id,
			number: number,
		});
		return {
			statusCode: 200,
			body: JSON.stringify({ tokens, ...rider }),
		};
	}
	return {
		statusCode: 401,
		body: JSON.stringify({
			message: "Invalid OTP",
		}),
	};
};
