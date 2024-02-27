const config = {
	streamKeyUrl: "http://session.com/auth/get_keys",
	getUserUrl: (user: string) => "http://session.com/get_user/" + user
}

export default config