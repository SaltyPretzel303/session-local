import User from "./User"


export interface AuthResponse {
	status: number
	message: string
	user: User
}

export function isSuccess(resp: AuthResponse) {
	return resp != null && resp != undefined && resp.status == 0
}