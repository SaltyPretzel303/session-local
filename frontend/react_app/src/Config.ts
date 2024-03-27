import { UserInfo } from "./Datas"
import Session from "supertokens-auth-react/recipe/session";

type configuration = {
	myRegion: string,

	userInfo: UserInfo | undefined,
	getUser: () => Promise<UserInfo | undefined>,
	// ^ this two above are still not used. They were intended to replace
	// userProvider methods propagated as a dependency trough the props

	streamKeyUrl: string,
	userUrl: (user: string) => string,
	streamInfoUrl: (stream: string, region: string) => string,
	allStreamsUrl: (start: number, count: number, region: string) => string,
	exploreStreamsUrl: (start: number, count: number, region: string) => string,
	recommendedStreamsUrl: (username: string,
		start: number,
		count: number,
		region: string) => string,
	userFromTokensIdUrl: (tokensId: string) => string,
	followingUrl: (username: string) => string,
	tnailUrl: (username: string) => string,
	notFoundTnailUrl: string
}


const config: configuration = {
	myRegion: 'eu',

	userInfo: undefined,

	getUser: async () => {
		if (config.userInfo != undefined) {
			console.log("User data already fetched, returning.")
			return config.userInfo
		}

		if (! await Session.doesSessionExist()) {
			console.log("Session doesn't exits.")
			return undefined
		}

		console.log("Session exits, will try to fetch user.")

		let userTokensId = await Session.getUserId()
		let infoUrl = config.userFromTokensIdUrl(userTokensId)
		// let requestInit = { method: 'GET' } as RequestInit

		let response = await fetch(infoUrl, { method: 'GET' })

		if (response.status != 200) {
			console.log("Return status not 200: " + await response.text)
			return undefined
		}

		config.userInfo = await response.json() as UserInfo

		return config.userInfo
	},

	streamKeyUrl: "http://session.com/auth/get_key",

	userUrl: (user: string) => `http://session.com/user/get_user/${user}`,

	streamInfoUrl: (streamer: string, region: string) =>
		`http://session.com/stream/stream_info/${streamer}?region=${region}`,

	allStreamsUrl: (start: number, count: number, region: string) =>

		`http://session.com/stream/all?
			region=${region}&
			start=${start}&
			count=${count}`,

	exploreStreamsUrl: (start: number, count: number, region: string) =>

		`http://session.com/stream/get_explore?
			region=${region || config.myRegion}&
			start=${start}&
			count=${count}`,

	recommendedStreamsUrl: (username: string,
		start: number,
		count: number,
		region: string) =>

		`http://session.com/stream/get_recommended/${username}?
			start=${start}&
			count=${count}&
			region=${region}`,

	userFromTokensIdUrl: (tokensId: string) =>
		`http://session.com/user/get_user_from_tokensid/${tokensId}`,

	followingUrl: (username: string) =>
		`http://session.com/user/get_following/${username}`,

	tnailUrl: (stream: string) => `http://session.com/stream/tnail/${stream}`,

	notFoundTnailUrl: "http://session.com/stream/tnail/unavailable"
}

export default config