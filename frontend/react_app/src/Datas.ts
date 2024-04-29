export type UserInfo = {
	username: string
	email: string
}

export type AuthResponse = {
	status: number
	message: string
	user: UserInfo
}

export function isAuthSuccess(resp: AuthResponse) {
	return resp != null && resp != undefined && resp.status == 0
}

export type MediaServer = {
	quality: string
	access_url: string
}

export enum StreamsOrdering {
	Views,
	Recommended,
	None
}

export type StreamInfo = {
	title: string
	creator: string
	category: string
	viewers: number
	media_servers: MediaServer[]
}

export function isKeySuccess(status: number) {
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

export type FollowingInfo = {
	username: string
	following: string
	from_date: string
}

export type UpdateRequest = {
	username: string
	title: string
	category: string
	is_public: boolean
}
