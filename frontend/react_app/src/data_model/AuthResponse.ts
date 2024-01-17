export interface AuthResponse {
	status: number
	username: string
	email: string
}

export function isSuccess(resp: AuthResponse) {
	return resp != null && resp != undefined && resp.status == 0
}