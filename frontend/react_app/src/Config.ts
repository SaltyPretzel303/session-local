import { StreamsOrdering } from "./Datas"

type configuration = {
	myRegion: string,

	streamKeyUrl: string,
	userUrl: (user: string) => string,
	streamInfoUrl: (stream: string, region: string) => string,
	allStreamsUrl: (start: number,
		count: number,
		region: string,
		ordering: StreamsOrdering) => string,

	exploreStreamsUrl: (start: number,
		count: number,
		region: string) => string,

	recommendedStreamsUrl: (username: string,
		start: number,
		count: number,
		region: string) => string,
	userFromTokensIdUrl: (tokensId: string) => string,
	followingUrl: string,
	tnailUrl: (username: string) => string,
	notFoundTnailUrl: string
}


const config: configuration = {
	myRegion: 'eu',

	streamKeyUrl: "http://session.com/auth/get_key",

	userUrl: (user: string) => `http://session.com/user/get_user/${user}`,

	streamInfoUrl: (streamer: string, region: string) =>
		`http://session.com/stream/stream_info/${streamer}?region=${region}`,

	allStreamsUrl: (start: number,
		count: number,
		region: string,
		ordering: StreamsOrdering) =>

		`http://session.com/stream/all?
			region=${region}&
			start=${start}&
			count=${count}&
			ordering=${ordering}`,

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

	followingUrl: `http://session.com/user/get_following`,

	tnailUrl: (stream: string) => `http://session.com/stream/tnail/${stream}`,

	notFoundTnailUrl: "http://session.com/stream/tnail/unavailable"
}

export default config