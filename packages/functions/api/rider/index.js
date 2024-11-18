import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { DynamoDBDocumentClient, GetCommand } from "@aws-sdk/lib-dynamodb";
import crypto from "crypto";
import { Table } from "sst/node/table";
import { findById, save, update } from "../common/db";
import { AdminCreateRider, utcDate } from "../auth";

const client = new DynamoDBClient({ region: "ap-south-1" });
const docClient = DynamoDBDocumentClient.from(client);

const ridersTable = Table.ridersTable.tableName;
const usersTable = Table.usersTable.tableName;

export const createRider = async (req) => {
	const id = crypto.randomUUID();
	const rider = {
		id: id,
		number: req.personalDetails.number,
		profileStatus: {},
		personalDetails: req.personalDetails,
		bankDetails: req.bankDetails,
		documents: req.documents.map(({ name, image }) => ({
			name,
			image,
			verified: "pending",
			rejectionReason: null,
		})),
		reviewStatus: "pending",
		submittedAt: new Date().toISOString(),
		updatedAt: new Date().toISOString(),
		accountVerified: false,
		role: "rider",
	};
	const date = new Date();
	const utc = utcDate(date);
	const res = await AdminCreateRider(req.personalDetails.number, id, utc);
	await save(usersTable, rider);
	return await findById(usersTable, id);
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
	const status = rider.profileStatus;
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

export const updateDocument = async (id, document) => {
	const rider = await get(id);
	const documents = rider.documents;
	const modDocs = documents.map((doc) =>
		doc.name === document.name ? { ...doc, document } : doc
	);
	return await update(
		usersTable,
		{
			id: id,
		},
		{
			documents: modDocs,
			updatedAt: new Date().toISOString(),
		}
	);
};
