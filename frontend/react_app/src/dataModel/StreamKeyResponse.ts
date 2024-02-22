
export function isSuccess(status: number) {
	return status == 0
}

export function failure(err: string): KeyResponse {
	return {
		status: 1,
		message: err
	} as KeyResponse
}

export type KeyResponse = {
	status: number
	message: string
	value: string
	exp_date: string
}