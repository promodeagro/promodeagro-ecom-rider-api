import { z } from "zod";
import middy from "@middy/core";
import { bodyValidator } from "../util/bodyValidator";
import { errorHandler } from "../util/errorHandler";
import { updatePersonal, updatebank, updateDocument, submitProfile } from ".";

const personalDetailsSchema = z.object({
	id: z.string().uuid(),
	fullName: z.string().min(3, "Full name is required"),
	dob: z.string().datetime(),
	email: z.string().email("Invalid email address"),
	address: z.object({
		address1: z.string().min(1, "Address 1 is required"),
		address2: z.string().optional(),
		landmark: z.string().optional(),
		state: z.string().min(1, "State is required"),
		city: z.string().min(1, "City is required"),
		pincode: z.string().min(5, "Pincode must be at least 5 characters"),
	}),
	reference: z.object({
		relation: z.string().min(1, "Relation is required"),
		number: z.string().regex(/^\d{10}$/, {
			message: "Invalid phone number. Must be exactly 10 digits.",
		}),
	}),
});

export const updatePersonalDetails = middy(async (event) => {
	const { id, ...req } = JSON.parse(event.body);
	return await updatePersonal(id, req);
})
	.use(bodyValidator(personalDetailsSchema))
	.use(errorHandler());

const bankDetailsSchema = z.object({
	id: z.string().uuid(),
	bankName: z.string().min(3, "Bank name must be at least 3 characters"),
	acc: z.string().min(1, "Account number is required"),
	ifsc: z.string().min(11, "IFSC code must be at least 11 characters"),
});

export const updatebankDetails = middy(async (event) => {
	const { id, ...req } = JSON.parse(event.body);
	return await updatebank(id, req);
})
	.use(bodyValidator(bankDetailsSchema))
	.use(errorHandler());

const documentSchema = z.object({
	id: z.string().uuid(),
	userPhoto: z.string().url("User photo must be a valid URL"),
	aadharFront: z.string().url("Aadhar front image must be a valid URL"),
	aadharBack: z.string().url("Aadhar back image must be a valid URL"),
	pan: z.string().url("PAN image must be a valid URL"),
	dl: z.string().url("Driving license image must be a valid URL"),
	vehicleImage: z.string().url("Vehicle image must be a valid URL"),
	rcBook: z.string().url("RC Book image must be a valid URL"),
});

export const updateDocumentDetails = middy(async (event) => {
	const { id, ...req } = JSON.parse(event.body);
	return await updateDocument(id, req);
})
	.use(bodyValidator(documentSchema))
	.use(errorHandler());

export const submitRiderProfile = middy(async (event) => {
	let id = event.pathParameters.id;
	if (!id) {
		return {
			status: 400,
			body: JSON.stringify({
				message: "invalid rider id",
			}),
		};
	}
	return await submitProfile(id);
})
	.use(errorHandler());
