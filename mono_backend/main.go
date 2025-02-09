package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"saltypretzel/session-backend/api"
	"saltypretzel/session-backend/api/auth"
	"saltypretzel/session-backend/api/controllers"
	"saltypretzel/session-backend/api/services"
	"saltypretzel/session-backend/config"
	"saltypretzel/session-backend/db"

	"github.com/supertokens/supertokens-golang/supertokens"
)

const CONFIG_FILE = "config.json"

func main() {

	fmt.Println("Starting web server.")

	cfg := config.Config{}
	config.WithFile(CONFIG_FILE, &cfg)
	config.WithEnv(&cfg)

	fmt.Println(" ====== CONFIG ====== ")
	bts, _ := json.MarshalIndent(cfg, " ", "    ")
	fmt.Println(string(bts))
	fmt.Println(" ====== CONFIG ====== ")

	err := auth.InitSuperTokens(cfg)
	if err != nil {
		fmt.Printf("error initializing supertokens: %v \n", err)
		os.Exit(1)
	}

	mux := http.NewServeMux()

	// ====== REPOSITORIES ======

	gormDb, err := db.GetPgresDb(cfg.Db)
	if err != nil {
		fmt.Println("failed to create db connection: ", err)
		os.Exit(1)
	}

	userRepo, err := db.NewUserRepo(gormDb)
	if err != nil {
		fmt.Println("failed to create gorm user repository, err: ", err)
		os.Exit(1)
	}

	_, err = db.NewChannelRepo(gormDb, userRepo)
	if err != nil {
		fmt.Println("failed to create gorm channel repository, err: ", err)
	}

	// ====== REPOSITORIES ======

	// ====== SERVICES ======

	userService := &services.UserService{
		UserDb: userRepo,
	}

	sessionProvider := auth.TokenSessionProvider{
		AuthProvider: userService,
	}

	// ====== SERVICES ======

	sessionProvider.MergeUsers(userService)
	// this will remove token users that have no data in my "custom" db

	// ====== CONTROLLERS ======

	uController := &controllers.UserController{
		BasePath:        "/user",
		UserService:     userService,
		SessionProvider: sessionProvider,
	}

	kController := &controllers.KeyController{
		Base:            "/key",
		SessionProvider: sessionProvider,
	}

	api.Apply(mux, cfg.ApiPrefix, uController)
	api.Apply(mux, cfg.ApiPrefix, kController)

	// ====== CONTROLLERS ======

	httpHandler := api.WithMiddleware(mux,
		api.WithCors,
		supertokens.Middleware)

	error := http.ListenAndServe(":80", httpHandler)
	if error != nil {
		fmt.Println("Error while listening: ", error)
	}

	fmt.Println("Web server is shutting down.")
}
