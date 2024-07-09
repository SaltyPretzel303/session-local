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

export type OrderingOption = {
	displayName: string
	value: Orderings
}

export enum Orderings {
	viewsAscending,
	viewsDescending,
	recommendedAscending,
	recommendedDescending,
	popularityAscending,
	popularityDescending,
	noOrder
}

export type StreamInfo = {
	title: string
	creator: string
	category: string
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

export type Category = {
	name: string
	display_name: string
}

export enum ChatMsgType {
	text,
	url,
	other
}

export type ChatMessage = {
	sender: string
	type: ChatMsgType
	txtContent: string
}

// export type SearchResult = {
// 	creator: string
// 	title: string | undefined
// 	category: string | undefined
// }