import middy from "@middy/core";
import { z } from "zod";
import { signout, signin, validateOtp, refreshTokens, packerSignin } from ".";
import { bodyValidator } from "../util/bodyValidator";
import { errorHandler } from "../util/errorHandler";

const phoneNumberSchema = z.object({
	number: z.string().regex(/^\d{10}$/, {
		message: "Invalid phone number. Must be exactly 10 digits.",
	}),
	// userType: z.enum(["rider"]),
});

export const signinHandler = middy(async (event) => {
	const req = JSON.parse(event.body);
	return await signin(req);
})
	.use(bodyValidator(phoneNumberSchema))
	.use(errorHandler());

const validateOtpSchema = z.object({
	number: phoneNumberSchema.shape.number,
	code: z.string().regex(/^\d{6}$/, {
		message: "Otp. Must be exactly 6 digits.",
	}),
	session: z.string(),
});

export const validateOtpHandler = middy(async (event) => {
	const body = JSON.parse(event.body);
	return await validateOtp(body);
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
	return refreshTokens(refreshToken);
})
	.use(bodyValidator(refreshTokenSchema))
	.use(errorHandler());

const signoutSchema = z.object({
	accessToken: z.string(),
});

export const signoutHandler = middy(async (event) => {
	const { accessToken } = JSON.parse(event.body);
	await signout(accessToken);
	return {
		statusCode: 200,
		body: JSON.stringify({
			message: "Successfully signed out",
		}),
	};
})
	.use(bodyValidator(signoutSchema))
	.use(errorHandler());

const emailSchema = z.string().email({ message: "invalid email" });

const packerSigninSchema = z.object({
	email: emailSchema,
	password: z.string(),
});

export const packerSigninHandler = middy(async (event) => {
	const req = JSON.parse(event.body);
	return await packerSignin(req);
})
	.use(bodyValidator(packerSigninSchema))
	.use(errorHandler());
