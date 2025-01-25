package main

import (
	"fmt"
	"net/http"
	"saltypretzel/session-backend/api"
	"saltypretzel/session-backend/api/auth"
	"saltypretzel/session-backend/api/controllers"
	"saltypretzel/session-backend/api/services"
	"saltypretzel/session-backend/db"

	"github.com/supertokens/supertokens-golang/supertokens"
)

func main() {
	fmt.Println("Starting web server.")

	auth.InitSetupTokens()

	mux := http.NewServeMux()

	// db, err := db.NewPostgre()
	// if err != nil {
	// 	fmt.Printf("Failed to connect to database: %v\n", err)
	// 	return
	// }

	db := db.NewFileUserRepository()

	userService := &services.UserService{
		Db: db,
	}

	sessionProvider := auth.TokenSessionProvider{
		UserService: *userService,
	}

	uController := &controllers.UserController{
		BasePath:        "/user",
		UserService:     userService,
		SessionProvider: sessionProvider,
	}

	uController.Route(mux)

	httpHandler := api.WithMiddleware(mux,
		api.WithCors,
		supertokens.Middleware)

	http.ListenAndServe(":80", httpHandler)

	fmt.Println("Web server is shutting down.")
}
