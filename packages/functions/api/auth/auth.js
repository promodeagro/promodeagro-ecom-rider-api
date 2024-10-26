import { z } from "zod";
import middy from "@middy/core";
import { bodyValidator } from "../util/bodyValidator";
import { errorHandler } from "../util/errorHandler";
import { numberExists, saveOtp, validateOtp } from ".";
import { createRider } from "../rider/index";
import { generateOtp, sendOtp } from "./sendOtp";
import { authorizer, refreshAccessToken } from "./jwt";

const phoneNumberSchema = z.object({
	number: z.string().regex(/^\d{10}$/, {
		message: "Invalid phone number. Must be exactly 10 digits.",
	}),
	userType: z.enum(["rider"]),
});

const createUser = async (number, otp, userType) => {
	if (userType === "rider") {
		return await createRider(number, otp);
	} else {
		return await createPacker(number, otp);
	}
};

export const signin = middy(async (event) => {
	const { number, userType } = JSON.parse(event.body);
	const item = await numberExists(number, userType);
	const otp = generateOtp();
	if (item && item.length > 0) {
		await saveOtp(item[0].id, otp, userType);
		await sendOtp(otp, number);
		return {
			statusCode: 200,
			body: JSON.stringify({
				message: "otp sent successfully",
			}),
		};
	}
	await createUser(number, otp, userType);
	await sendOtp(otp, number);
	return {
		statusCode: 200,
		body: JSON.stringify({
			message: "rider crerated  successfully",
		}),
	};
})
	.use(bodyValidator(phoneNumberSchema))
	.use(errorHandler());

const validateOtpSchema = z.object({
	number: phoneNumberSchema.shape.number,
	otp: z.string().regex(/^\d{6}$/, {
		message: "Otp. Must be exactly 6 digits.",
	}),
	userType: z.enum(["rider", "packer"]),
});

export const validateOtpHandler = middy(async (event) => {
	const { otp, number, userType } = JSON.parse(event.body);
	return validateOtp(otp, number, userType);
})
	.use(bodyValidator(validateOtpSchema))
	.use(errorHandler());

export const authorizerHandler = async (event) => {
	return authorizer(event);
};

const refreshTokenSchema = z.object({
	refreshToken: z.string(),
});

export const refreshAccessTokenHandler = middy(async (event) => {
	const { refreshToken } = JSON.parse(event.body);
	return refreshAccessToken(refreshToken);
})
	.use(bodyValidator(refreshTokenSchema))
	.use(errorHandler());
