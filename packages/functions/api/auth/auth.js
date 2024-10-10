import { number, z } from "zod";
import middy from "@middy/core";
import { bodyValidator } from "../util/bodyValidator";
import { errorHandler } from "../util/errorHandler";
import { numberExists, saveOtp, validateOtp } from ".";
import { createRider } from "../rider/index";
import { generateOtp, sendOtp } from "./sendOtp";

const phoneNumberSchema = z.object({
	number: z.string().regex(/^\d{10}$/, {
		message: "Invalid phone number. Must be exactly 10 digits.",
	}),
});

export const signin = middy(async (event) => {
	const { number } = JSON.parse(event.body);
	const item = await numberExists(number);
	const otp = generateOtp();
	if (item && item.length > 0) {
		await saveOtp(item[0].id, otp);
		await sendOtp(otp, number);
		return {
			statusCode: 200,
			body: JSON.stringify({
				message: "otp sent successfully",
			}),
		};
	}
	await createRider(number, otp);
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
});

export const validateOtpHandler = middy(async (event) => {
	const { otp, number } = JSON.parse(event.body);

	return validateOtp(otp, number);
})
	.use(bodyValidator(validateOtpSchema))
	.use(errorHandler());
