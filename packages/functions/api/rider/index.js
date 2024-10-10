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
			documentsCompleted: false,
		}),
		personalDetails: "{}",
		bankDetails: "{}",
		documents: "{}",
		reviewStatus: "not_submitted",
		submittedAt: null,
		accountVerified: false,
	};
	return await save(riderTable, rider);
};

export const get = async (id) => {
	const params = {
		TableName: riderTable,
		Key: {
			id: id,
		},
	};
	const result = await docClient.send(new GetCommand(params));
	return result.Item;
};

export const updatePersonal = async (id, item) => {
	const rider = await get(id);
	console.log("rider ", rider);
	const status = JSON.parse(rider.profileStatus);
	status.personalInfoCompleted = true;
	const updatedStatus = JSON.stringify(status);
	return await update(
		riderTable,
		{
			id: id,
		},
		{
			personalDetails: JSON.stringify(item),
			profileStatus: updatedStatus,
			updatedAt: new Date().toISOString(),
		}
	);
};

export const updatebank = async (id, item) => {
	const rider = await get(id);
	const status = JSON.parse(rider.profileStatus);
	status.bankDetailsCompleted = true;
	const updatedStatus = JSON.stringify(status);
	return await update(
		riderTable,
		{
			id: id,
		},
		{
			bankDetails: JSON.stringify(item),
			profileStatus: updatedStatus,
			updatedAt: new Date().toISOString(),
		}
	);
};

export const updateDocument = async (id, item) => {
	const rider = await get(id);
	const status = JSON.parse(rider.profileStatus);
	status.documentsCompleted = true;
	const updatedStatus = JSON.stringify(status);
	return await update(
		riderTable,
		{
			id: id,
		},
		{
			documents: JSON.stringify(item),
			profileStatus: updatedStatus,
			updatedAt: new Date().toISOString(),
		}
	);
};

export const submitProfile = async (id) => {
	const rider = await get(id);
	const status = JSON.parse(rider.profileStatus);
	if (
		status.personalInfoCompleted &&
		status.bankDetailsCompleted &&
		status.documentsCompleted
	) {
		return await update(
			riderTable,
			{ id: id },
			{
				reviewStatus: "pending",
				submittedAt: new Date().toISOString(),
				updatedAt: new Date().toISOString(),
			}
		);
	}
	return {
		statusCode: 400,
		body: JSON.stringify({
			message: "need to completed profile first",
		}),
	};
};
