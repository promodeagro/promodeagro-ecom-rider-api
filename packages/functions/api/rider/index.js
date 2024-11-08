import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import {
	DynamoDBDocumentClient,
	GetCommand
} from "@aws-sdk/lib-dynamodb";
import crypto from "crypto";
import { Table } from "sst/node/table";
import { save, update } from "../common/db";

const client = new DynamoDBClient({ region: "ap-south-1" });
const docClient = DynamoDBDocumentClient.from(client);

const ridersTable = Table.ridersTable.tableName;
const usersTable = Table.usersTable.tableName;

export const createRider = async (number) => {
	const id = crypto.randomUUID();
	const rider = {
		id: id,
		number: number,
		profileStatus: {
			personalInfoCompleted: false,
			bankDetailsCompleted: false,
			documentsCompleted: false,
		},
		personalDetails: {},
		bankDetails: {},
		documents: {},
		reviewStatus: "not_submitted",
		submittedAt: null,
		accountVerified: false,
	};
	return await save(usersTable, rider);
};

export const get = async (id) => {
	const params = {
		TableName: usersTable,
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
	const status = rider.profileStatus;
	status.personalInfoCompleted = true;
	return await update(
		usersTable,
		{
			id: id,
		},
		{
			personalDetails: item,
			profileStatus: status,
			updatedAt: new Date().toISOString(),
		}
	);
};

export const updatebank = async (id, item) => {
	item.status = "pending";
	const rider = await get(id);
	const status = rider.profileStatus;
	status.bankDetailsCompleted = true;
	return await update(
		usersTable,
		{
			id: id,
		},
		{
			bankDetails: item,
			profileStatus: status,
			updatedAt: new Date().toISOString(),
		}
	);
};

export const updateDocument = async (id, documents) => {
	const rider = await get(id);
	const status = rider.profileStatus;
	status.documentsCompleted = true;
	const modDocs = documents.map(({ name, image }) => ({
		name,
		image,
		verified: "pending",
		rejectionReason: null,
	}));
	return await update(
		usersTable,
		{
			id: id,
		},
		{
			documents: modDocs,
			profileStatus: status,
			updatedAt: new Date().toISOString(),
		}
	);
};

export const submitProfile = async (id) => {
	const rider = await get(id);
	const status = rider.profileStatus;
	if (
		status.personalInfoCompleted &&
		status.bankDetailsCompleted &&
		status.documentsCompleted
	) {
		return await update(
			usersTable,
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
