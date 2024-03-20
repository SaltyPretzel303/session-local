const config = {
	region: 'eu',
	streamKeyUrl: "http://session.com/auth/get_key",

	userUrl: (user: string) => "http://session.com/user/get_user/" + user,

	streamInfoUrl: (streamer: string, region: string) =>
		"http://session.com/stream/stream_info/" + streamer + "?region=" + region,

	exploreStreamsUrl: "http://session.com/stream/get_explore/",

	recommendedStreamsUrl: (username: string) =>
		"http://session.com/stream/get_recommended/" + username,

	userFromTokensIdUrl: (tokensId: string) =>
		"http://session.com/user/get_user_from_tokensid/" + tokensId,

	followingUrl: (username: string) =>
		"http://session.com/user/get_following/" + username,

	tnailUrl: (stream: string) => "http://session.com/stream/tnail/" + stream,

	notFoundTnailUrl: () => "http://session.com/stream/tnail/unavailable"
}

export default config