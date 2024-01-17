export default interface User {
	username: string
	email: string

	following: string[] // list of usernames
}