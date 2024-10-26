import jwt from "jsonwebtoken";
import { Config } from "sst/node/config";

export const generateAccessToken = (payload, signOptions) =>
	jwt.sign(payload, Config.JWT_SECRET, signOptions);

export const generateRefreshToken = (payload, signOptions) =>
	jwt.sign(payload, Config.JWT_REFRESH_SECRET, signOptions);

export const verifyAccessToken = (token) =>
	jwt.verify(token, Config.JWT_SECRET);

export const verifyRefreshToken = (token) =>
	jwt.verify(token, Config.JWT_REFRESH_SECRET);

export const decodeToken = (token) => jwt.decode(token);

export const generateTokens = (payload) => {
	var signOptions = {
		issuer: "https://www.rider.promodeagro.com/",
		subject: payload.id,
		expiresIn: "1d",
	};
	const accessToken = generateAccessToken(payload, signOptions);
	const refreshToken = generateRefreshToken(payload, signOptions);
	return { accessToken, refreshToken };
};

export const refreshAccessToken = (refreshToken) => {
	const decoded = verifyRefreshToken(refreshToken);
	return generateTokens({
		id: decoded.id,
		number: decoded.number,
	});
};

export const authorizer = async (event) => {
	try {
		const token = event.authorizationToken.replace("Bearer ", "");
		const decoded = jwt.verify(token, Config.JWT_SECRET);
		const userType = decoded.userType;
		let effect = "Deny";
		if (userType === "rider" && event.methodArn.includes("/rider")) {
			effect = "Allow";
		}
		if (userType === "packer" && event.methodArn.includes("/packer")) {
			effect = "Allow";
		}
		return {
			principalId: decoded.id,
			policyDocument: {
				Version: "2012-10-17",
				Statement: [
					{
						Action: "execute-api:Invoke",
						Effect: effect,
						Resource: event.methodArn,
					},
				],
			},
			context: {
				userId: decoded.id,
				number: decoded.number,
				userType: decoded.userType,
			},
		};
	} catch (error) {
		console.error("JWT Verification failed:", error);
		return {
			principalId: "user",
			policyDocument: {
				Version: "2012-10-17",
				Statement: [
					{
						Action: "execute-api:Invoke",
						Effect: effect,
						Resource: event.methodArn,
					},
				],
			},
		};
	}
};
