import { z } from "zod";
import middy from "@middy/core";
import { bodyValidator } from "../util/bodyValidator";
import { errorHandler } from "../util/errorHandler";
import { updatePersonal, updatebank, updateDocument, createRider } from ".";

const bankDetailsSchema = z.object({
	bankName: z.string().min(3, "Bank name must be at least 3 characters"),
	acc: z.string().min(1, "Account number is required"),
	ifsc: z.string().min(11, "IFSC code must be at least 11 characters"),
});

const documentSchema = z.object({
	document: z.object({
		name: z.string(),
		image: z.string().url(),
	}),
});

const personalDetailsSchema = z.object({
	fullName: z.string().min(3, "Full name is required"),
	dob: z.string().datetime(),
	email: z.string().email("Invalid email address"),
	number: z.string().regex(/^\d{10}$/, {
		message: "Invalid phone number. Must be exactly 10 digits.",
	}),
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

const riderSchema = z.object({
	personalDetails: personalDetailsSchema,
	bankDetails: bankDetailsSchema,
	documents: z.array(
		z.object({
			name: z.string(),
			image: z.string().url(),
		})
	),
});

export const createRiderHandler = middy(async (event) => {
	const req = JSON.parse(event.body);
	return await createRider(req);
})
	.use(bodyValidator(riderSchema))
	.use(errorHandler());

export const updatePersonalDetails = middy(async (event) => {
	const { id, ...req } = JSON.parse(event.body);
	return await updatePersonal(id, req);
})
	.use(bodyValidator(personalDetailsSchema))
	.use(errorHandler());

export const updatebankDetails = middy(async (event) => {
	const { id, ...req } = JSON.parse(event.body);
	return await updatebank(id, req);
})
	.use(bodyValidator(bankDetailsSchema))
	.use(errorHandler());

export const updateDocumentDetails = middy(async (event) => {
	const { id, document } = JSON.parse(event.body);
	return await updateDocument(id, documents);
})
	.use(bodyValidator(documentSchema))
	.use(errorHandler());
