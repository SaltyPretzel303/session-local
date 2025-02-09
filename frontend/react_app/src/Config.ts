import { Orderings } from "./Datas"

const DOMAIN = 'session.com'
const PREFIX = 'api/v1'

type configuration = {
	myRegion: string,
	domainName: string,

	streamKeyUrl: string,
	userByUsernameUrl: (user: string) => string,
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

	categoryStreamsUrl: (category: string,
		start: number,
		count: number,
		region: string) => string,

	userFromTokensIdUrl: (tokensId: string) => string,
	followingUrl: (from: number, count: number, ordering: Orderings) => string,
	tnailUrl: (username: string) => string,
	notFoundTnailUrl: string,
	previewQuality: string,
	viewCountUrl: (stream: string) => string,
	isLiveUrl: (stramer: string) => string,
	categoriesUrl: string,
	categoriesRangeUrl: (start: number, count: number) => string,
	lowCategoryIconUrl: (name: string) => string,
	highCategoryIconUrl: (name: string) => string,
	updateStreamUrl: string,
	chatRelayUrl: (channel: string) => string,
	streamSearchUrl: (query: string,
		start: number,
		count: number,
		region: string) => string
	isFollowingUrl: (followed: string) => string
	followUrl: (channel: string) => string
	unfollowUrl: (channel: string) => string
}

const oldConfig: configuration = {
	myRegion: 'eu',

	domainName: 'session.com',

	streamKeyUrl: `http://${DOMAIN}/auth/get_key`,
	userByUsernameUrl: (user: string) => `http://${DOMAIN}/user/get_user/${user}`,
	streamInfoUrl: (streamer: string, region: string) =>
		`http://${DOMAIN}/stream/stream_info/${streamer}?region=${region}`,

	allStreamsUrl: (start: number,
		count: number,
		region: string,
		ordering: Orderings) =>

		`http://${DOMAIN}/stream/all?
			region=${region}&
			start=${start}&
			count=${count}&
			ordering=${ordering.toString()}`,

	exploreStreamsUrl: (start: number, count: number, region: string) =>
		`http://${DOMAIN}/stream/get_explore?
			region=${region || config.myRegion}&
			start=${start}&
			count=${count}`,

	recommendedStreamsUrl: (username: string,
		start: number,
		count: number,
		region: string) =>

		`http://${DOMAIN}/stream/get_recommended/${username}?
			start=${start}&
			count=${count}&
			region=${region}`,
	categoryStreamsUrl: (category: string,
		start: number,
		count: number,
		region: string) =>
		`http://${DOMAIN}/stream/by_category/${category}?
					start=${start}&
					count=${count}&
					region=${region}`,

	userFromTokensIdUrl: (tokensId: string) =>
		`http://${DOMAIN}/user/get_user_from_tokensid/${tokensId}`,

	followingUrl: (start, count, ordering) =>
		`http://${DOMAIN}/user/get_following?
				start=${start}&
				count=${count}&
				oredering=${ordering.toString()}`,

	tnailUrl: (stream: string) => `http://${DOMAIN}/stream/tnail/${stream}`,

	notFoundTnailUrl: `http://${DOMAIN}/stream/tnail/unavailable`,
	previewQuality: "preview",
	viewCountUrl: (stream: string) => `http://${DOMAIN}/stream/viewer_count/${stream}`,
	isLiveUrl: (streamer: string) => `http://${DOMAIN}/stream/is_live/${streamer}`,
	categoriesUrl: `http://${DOMAIN}/stream/categories`,
	categoriesRangeUrl: (f, t) => `http://${DOMAIN}/stream/categories?start=${f}&end=${t}`,
	lowCategoryIconUrl: (name: string) =>
		`http://${DOMAIN}/stream/category_low_tnail/${name}`,
	highCategoryIconUrl: (name: string) =>
		`http://${DOMAIN}/stream/category_high_tnail/${name}`,
	updateStreamUrl: `http://${DOMAIN}/stream/update`,
	chatRelayUrl: (channel) => `ws://${DOMAIN}/chat/${channel}`,
	streamSearchUrl: (query, start, count, region) =>
		`http://session.com/stream/stream_query/${query}?
													start=${start}&
													count=${count}&
													region=${region}`,
	isFollowingUrl: (followed: string) => `http://${DOMAIN}/user/is_following/${followed}`,
	followUrl: (channel: string) => `http://${DOMAIN}/user/follow/${channel}`,
	unfollowUrl: (channel: string) => `http://${DOMAIN}/user/unfollow/${channel}`
}

const newConfig: configuration = {
	myRegion: 'eu',

	domainName: 'session.com',

	streamKeyUrl: `http://${DOMAIN}/${PREFIX}/auth/get_key`,
	userByUsernameUrl: (username: string) =>
		`http://${DOMAIN}/${PREFIX}/user/username?username=${username}`,
	streamInfoUrl: (streamer: string, region: string) =>
		`http://${DOMAIN}/${PREFIX}/stream/stream_info/${streamer}?region=${region}`,

	allStreamsUrl: (start: number,
		count: number,
		region: string,
		ordering: Orderings) =>

		`http://${DOMAIN}/${PREFIX}/stream/all?
			region=${region}&
			start=${start}&
			count=${count}&
			ordering=${ordering.toString()}`,

	exploreStreamsUrl: (start: number, count: number, region: string) =>
		`http://${DOMAIN}/${PREFIX}/stream/get_explore?
			region=${region || config.myRegion}&
			start=${start}&
			count=${count}`,

	recommendedStreamsUrl: (username: string,
		start: number,
		count: number,
		region: string) =>

		`http://${DOMAIN}/${PREFIX}/stream/get_recommended/${username}?
			start=${start}&
			count=${count}&
			region=${region}`,
	categoryStreamsUrl: (category: string,
		start: number,
		count: number,
		region: string) =>
		`http://${DOMAIN}/${PREFIX}/stream/by_category/${category}?
					start=${start}&
					count=${count}&
					region=${region}`,

	userFromTokensIdUrl: (tokensId: string) =>
		`http://${DOMAIN}/${PREFIX}/user/token?token=${tokensId}`,

	followingUrl: (start, count, ordering) =>
		`http://${DOMAIN}/${PREFIX}/user/get_following?
				start=${start}&
				count=${count}&
				oredering=${ordering.toString()}`,

	tnailUrl: (stream: string) => `http://${DOMAIN}/${PREFIX}/stream/tnail/${stream}`,

	notFoundTnailUrl: `http://${DOMAIN}/${PREFIX}/stream/tnail/unavailable`,
	previewQuality: "preview",
	viewCountUrl: (stream: string) => `http://${DOMAIN}/${PREFIX}/stream/viewer_count/${stream}`,
	isLiveUrl: (streamer: string) => `http://${DOMAIN}/${PREFIX}/stream/is_live/${streamer}`,
	categoriesUrl: `http://${DOMAIN}/${PREFIX}/stream/categories`,
	categoriesRangeUrl: (f, t) => `http://${DOMAIN}/${PREFIX}/stream/categories?start=${f}&end=${t}`,
	lowCategoryIconUrl: (name: string) =>
		`http://${DOMAIN}/${PREFIX}/stream/category_low_tnail/${name}`,
	highCategoryIconUrl: (name: string) =>
		`http://${DOMAIN}/${PREFIX}/stream/category_high_tnail/${name}`,
	updateStreamUrl: `http://${DOMAIN}/${PREFIX}/stream/update`,
	chatRelayUrl: (channel) => `ws://${DOMAIN}/${PREFIX}/chat/${channel}`,
	streamSearchUrl: (query, start, count, region) =>
		`http://session.com/stream/stream_query/${query}?
													start=${start}&
													count=${count}&
													region=${region}`,
	isFollowingUrl: (followed: string) => `http://${DOMAIN}/${PREFIX}/user/is_following/${followed}`,
	followUrl: (channel: string) => `http://${DOMAIN}/${PREFIX}/user/follow/${channel}`,
	unfollowUrl: (channel: string) => `http://${DOMAIN}/${PREFIX}/user/unfollow/${channel}`
}


const config: configuration = newConfig

export default config