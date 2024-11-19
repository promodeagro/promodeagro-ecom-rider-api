import {
	AdminCreateUserCommand,
	AdminInitiateAuthCommand,
	CognitoIdentityProviderClient,
	GlobalSignOutCommand,
	InitiateAuthCommand,
	RespondToAuthChallengeCommand,
} from "@aws-sdk/client-cognito-identity-provider";
import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { DynamoDBDocumentClient, QueryCommand } from "@aws-sdk/lib-dynamodb";
import jwt from "jsonwebtoken";
import { Table } from "sst/node/table";
import { findById } from "../common/db";

const client = new DynamoDBClient({ region: "ap-south-1" });
const docClient = DynamoDBDocumentClient.from(client);

const cognitoClient = new CognitoIdentityProviderClient({
	region: "ap-south-1",
});

const usersTable = Table.usersTable.tableName;

export const numberExists = async (number) => {
	const params = {
		TableName: usersTable,
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

export const validateOtp = async ({ number, code, session }) => {
	// Verify OTP
	const command = new RespondToAuthChallengeCommand({
		ClientId: process.env.COGNITO_CLIENT,
		ChallengeName: "CUSTOM_CHALLENGE",
		Session: session,
		ChallengeResponses: {
			USERNAME: `+91${number}`,
			ANSWER: code,
		},
	});

	const response = await cognitoClient.send(command);
	if (!response.AuthenticationResult) {
		return {
			statusCode: 400,
			body: JSON.stringify({
				message: "Invalid OTP, please try again",
				session: response.Session, // Return new session for retry
			}),
		};
	}
	const idTokenDocoded = jwt.decode(response.AuthenticationResult?.IdToken);
	const user = await findById(usersTable, idTokenDocoded["custom:userId"]);
	return {
		statusCode: 200,
		body: JSON.stringify({
			message: "Signed in successfully",
			user: user,
			tokens: {
				accessToken: response.AuthenticationResult?.AccessToken,
				idToken: response.AuthenticationResult?.IdToken,
				refreshToken: response.AuthenticationResult?.RefreshToken,
			},
		}),
	};
};

export const signin = async ({ number }) => {
	const response = await initiateAuth(number);
	return {
		statusCode: 200,
		body: JSON.stringify({
			message: "OTP sent successfully",
			session: response.Session,
		}),
	};
};

export const AdminCreateRider = async (number, id, date) => {
	const createCommand = new AdminCreateUserCommand({
		UserPoolId: process.env.USER_POOL_ID,
		Username: `+91${number}`,
		UserAttributes: [
			{ Name: "phone_number", Value: `+91${number}` },
			{ Name: "custom:userId", Value: id },
			{ Name: "custom:role", Value: "rider" },
			{ Name: "custom:createdAt", Value: date },
			{ Name: "phone_number_verified", Value: "true" },
		],
		MessageAction: "SUPPRESS",
	});
	return await cognitoClient.send(createCommand);
};

const initiateAuth = async (number) => {
	const command = new AdminInitiateAuthCommand({
		AuthFlow: "CUSTOM_AUTH",
		UserPoolId: process.env.USER_POOL_ID,
		ClientId: process.env.COGNITO_CLIENT,
		AuthParameters: {
			USERNAME: `+91${number}`,
		},
	});
	return await cognitoClient.send(command);
};

export const utcDate = (date) => {
	const year = date.getUTCFullYear();
	const month = String(date.getUTCMonth() + 1).padStart(2, "0"); // Months are zero-based
	const day = String(date.getUTCDate()).padStart(2, "0");
	const hours = String(date.getUTCHours()).padStart(2, "0");
	const minutes = String(date.getUTCMinutes()).padStart(2, "0");
	const seconds = String(date.getUTCSeconds()).padStart(2, "0");

	return `${year}-${month}-${day} ${hours}:${minutes}:${seconds} UTC`;
};

export const refreshTokens = async (refreshToken) => {
	const command = new AdminInitiateAuthCommand({
		AuthFlow: "REFRESH_TOKEN_AUTH",
		UserPoolId: process.env.USER_POOL_ID,
		ClientId: process.env.COGNITO_CLIENT,
		AuthParameters: {
			REFRESH_TOKEN: refreshToken,
		},
	});
	const res = await cognitoClient.send(command);
	return {
		accessToken: res.AuthenticationResult.AccessToken,
		idToken: res.AuthenticationResult.AccessToken,
		expiresIn: res.AuthenticationResult.ExpiresIn,
	};
};

export const signout = async (accessToken) => {
	const signOutParams = {
		AccessToken: accessToken,
	};
	const command = new GlobalSignOutCommand(signOutParams);
	await cognitoClient.send(command);
};

export const packerSignin = async ({ email, password }) => {
	const authResponse = await initiateEmailAuth({ email, password });
	const accessToken = authResponse.AuthenticationResult?.AccessToken;
	const idToken = authResponse.AuthenticationResult?.IdToken;
	const refreshToken = authResponse.AuthenticationResult?.RefreshToken;

	const decodedHeader = jwt.decode(idToken, { complete: true });
	if (!(decodedHeader.payload["custom:role"] === "packer")) {
		return {
			statusCode: 403,
			body: "Unauthorized",
		};
	}
	return {
		statusCode: 200,
		body: JSON.stringify({
			accessToken: accessToken,
			idToken: idToken,
			refreshToken: refreshToken,
		}),
	};
};

const initiateEmailAuth = async ({ email, password }) => {
	console.log(process.env.USER_POOL_ID);
	console.log(process.env.COGNITO_CLIENT);
	const authParams = {
		AuthFlow: "USER_PASSWORD_AUTH",
		UserPoolId: process.env.USER_POOL_ID,
		ClientId: process.env.COGNITO_CLIENT,
		AuthParameters: {
			USERNAME: email,
			PASSWORD: password,
		},
	};
	const authCommand = new InitiateAuthCommand(authParams);
	return await cognitoClient.send(authCommand);
};
