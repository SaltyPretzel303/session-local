import { resolve } from "path";
import config from './Config'

// export function validEmail(value: string | undefined) {
// 	return (value != undefined && !value.includes(" "))
// }

// export function validUsername(value: string | undefined) {
// 	return (value != undefined && !value.includes(" "))
// }

// Method returns error message, thus undefined indicates username is valid
export async function validUsername(username: string): Promise<string | undefined> {
	console.log("Doing username validation for: " + username)
	let valid = true // perfrom some frontend logic for this

	if (!valid) {
		return "Username invalid."
	}

	try {
		let res = await fetch(config.getUserUrl(username))

		if (res.status == 200) {
			console.log("User found, username not unique.")
			return "Username already in use."
		} else {
			console.log("Username not found, username is unique.")
			return undefined
		}

	} catch (e) {
		console.log("Get user request failed with: " + e)
		return "Failed to check username."
	}
}

// export function matchingPwd(value_1: string | undefined, value_2: string | undefined) {
// 	// return (value_1 !== undefined && value_2 !== undefined && value_1 === value_2)
// 	return true
// }

// export function anyClear(inputs: (HTMLInputElement | null)[]) {
// 	return inputs.find((inEl) => {
// 		return inEl != null &&
// 			inEl.value != undefined &&
// 			inEl.value == ""
// 	}) != null;
// }

export function anyClear(values: string[]) {
	return values.find((el) => el === undefined || el === "")
}