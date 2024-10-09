import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import {
	DynamoDBDocumentClient,
	PutCommand,
	ScanCommand,
	GetCommand,
	UpdateCommand,
	QueryCommand,
} from "@aws-sdk/lib-dynamodb";

const client = new DynamoDBClient();
const docClient = DynamoDBDocumentClient.from(client);

export async function update(tableName, key, updateData) {
	const updateExpression = [];
	const expressionAttributeValues = {};
	const expressionAttributeNames = {};

	Object.keys(updateData).forEach((attr, index) => {
		updateExpression.push(`#attr${index} = :val${index}`);
		expressionAttributeNames[`#attr${index}`] = attr;
		expressionAttributeValues[`:val${index}`] = updateData[attr];
	});

	const params = {
		TableName: tableName,
		Key: key,
		UpdateExpression: `SET ${updateExpression.join(", ")}`,
		ExpressionAttributeNames: expressionAttributeNames,
		ExpressionAttributeValues: expressionAttributeValues,
		ReturnValues: "ALL_NEW",
	};

	const command = new UpdateCommand(params);
	const response = await docClient.send(command);
	return response.Attributes;
}

export async function save(tableName, item) {
	const timestamp = new Date().toISOString();
	item = { ...item, createdAt: timestamp, updatedAt: timestamp };
	const params = {
		TableName: tableName,
		Item: item,
	};
	await docClient.send(new PutCommand(params));
}
