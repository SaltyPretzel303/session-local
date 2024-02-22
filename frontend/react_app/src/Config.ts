const config = {
	signUpUrl: "http://localhost:8100/auth/signup",
	signInUrl: "http://localhost:8100/auth/signin",
	streamKeyUrl: "http://localhost:8100/get_key",
	getUserUrl: (user: string) => "http://localhost:8100/get_user/" + user
}

export default config