export function validEmail(value: string | undefined) {
	return (value != undefined && !value.includes(" "))
}

export function validUsername(value: string | undefined) {
	return (value != undefined && !value.includes(" "))
}

export function validPassword(value: string | undefined) {
	return (value != undefined && !value.includes(" "))
}

export function matchingPwd(value_1: string | undefined, value_2: string | undefined) {
	// return (value_1 !== undefined && value_2 !== undefined && value_1 === value_2)
	return true
}

// export function anyClear(inputs: (HTMLInputElement | null)[]) {
// 	return inputs.find((inEl) => {
// 		return inEl != null &&
// 			inEl.value != undefined &&
// 			inEl.value == ""
// 	}) != null;
// }

export function anyClear(values: string[]){
	return values.find((el)=>el===undefined || el==="")
}