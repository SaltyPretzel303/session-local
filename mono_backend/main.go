package main

import (
	"fmt"
	"net/http"
	"saltypretzel/session-backend/api"
	"saltypretzel/session-backend/data"
)

func main() {
	fmt.Println("Starting web server.")

	api.SetupTokens()

	mux := http.NewServeMux()
	api.HandleUnprotected(mux, "/", func(rw http.ResponseWriter, r *http.Request) {
		fmt.Println("main handler")
	})

	api.HandleProtected(mux, "/user", func(rw http.ResponseWriter, r *http.Request, user data.User) {
		fmt.Println("protected handler")
		fmt.Printf("%+v", user)
	})

	api.Listen(mux)

	fmt.Println("Web server is shutting down.")
}
