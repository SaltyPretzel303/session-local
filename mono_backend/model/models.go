package model

type User struct {
	Username string `json:"username"`
	Email    string `json:"email"`
}

type Channel struct {
	Name        string
	Description string
}

type QueryRange struct {
	From  int
	Count int
}
