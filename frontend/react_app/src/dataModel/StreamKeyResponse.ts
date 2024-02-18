
export function isSuccess(status: number) {
	return status == 0
}

export type KeyResponse = {
	status: number
	message: string
	value: string
	exp_data: string
}