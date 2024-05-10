import { Orderings } from "./Datas"

type configuration = {
	myRegion: string,

	streamKeyUrl: string,
	userUrl: (user: string) => string,
	streamInfoUrl: (stream: string, region: string) => string,
	allStreamsUrl: (start: number,
		count: number,
		region: string,
		ordering: Orderings) => string,

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
	notFoundTnailUrl: string,
	previewQuality: string,
	viewCountUrl: (stream: string) => string,
	isLiveUrl: (stramer: string) => string,
	categoriesUrl: string,
	categoriesRangeUrl: (fromInd: number, toInd: number) => string,
	lowCategoryIconUrl: (name: string) => string,
	highCategoryIconUrl: (name: string) => string,
	updateStreamUrl: string
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
		ordering: Orderings) =>

		`http://session.com/stream/all?
			region=${region}&
			start=${start}&
			count=${count}&
			ordering=${ordering.toString()}`,

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

	notFoundTnailUrl: "http://session.com/stream/tnail/unavailable",
	previewQuality: "preview",
	viewCountUrl: (stream: string) => `http://session.com/stream/viewer_count/${stream}`,
	isLiveUrl: (streamer: string) => `http://session.com/stream/is_live/${streamer}`,
	categoriesUrl: "http://session.com/stream/categories",
	categoriesRangeUrl: (f, t) => `http://session.com/stream/categories?start=${f}&end=${t}`,
	lowCategoryIconUrl: (name: string) =>
		"http://session.com/stream/category_low_tnail/" + name,
	highCategoryIconUrl: (name: string) =>
		"http://session.com/stream/category_high_tnail/" + name,
	updateStreamUrl: "http://session.com/stream/update"
}

export default config