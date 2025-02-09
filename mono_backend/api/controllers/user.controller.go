package controllers

import (
	"encoding/json"
	"fmt"
	"net/http"
	"saltypretzel/session-backend/api"
	"saltypretzel/session-backend/api/services"
	"saltypretzel/session-backend/model"
)

const (
	KEY_ARG = "req_key"
)

type UserController struct {
	BasePath        string
	UserService     *services.UserService
	SessionProvider api.ISessionProvider
}

func (uc *UserController) GetBasePath() string {
	return uc.BasePath
}

func (uc *UserController) getByUsername(resp http.ResponseWriter, r *http.Request) {
	fmt.Println("Processing api ... ")
	username := r.URL.Query().Get("username")
	// username := r.Form.Get("username")
	user, err := uc.UserService.GetUserByUsername(username)

	fmt.Println("Processing get user by username: ", username)

	if err != nil {
		resp.WriteHeader(http.StatusInternalServerError)
		resp.Write([]byte("Error"))
		return
	}

	rData, err := json.Marshal(user)
	if err != nil {
		resp.WriteHeader(http.StatusInternalServerError)
		resp.Write([]byte("Error"))
		return
	}

	resp.Write([]byte(rData))
}

func (uc *UserController) getByToken(resp http.ResponseWriter, r *http.Request) {
	// token := r.Form.Get("token")

	token := r.URL.Query().Get("token")
	fmt.Println("Procession get user by tokensid: ", token)

	resp.Write([]byte("GetUserByToken"))
}

func (uc *UserController) isAuthenticated(resp http.ResponseWriter, r *http.Request, user model.User) {
	// Since this is should be protected route, if the request si not denied by
	// the middleware ... user is authenticated/has_session.
	resp.WriteHeader(http.StatusOK)
}

func (uc *UserController) getFollowing(resp http.ResponseWriter, r *http.Request, user model.User) {
	resp.Write([]byte("GetFollowedChannels"))
}

func (uc *UserController) isFollowing(resp http.ResponseWriter, r *http.Request, user model.User) {
	// r.whom
	resp.Write([]byte("GetUserByToken"))
}

func (uc *UserController) removeUser(resp http.ResponseWriter, r *http.Request) {
	// r.username
	resp.Write([]byte("RemoveUser"))
}

func (uc *UserController) authorizeView(resp http.ResponseWriter, r *http.Request, user model.User) {
	// headers.get("X-Stream-Username")
	resp.Write([]byte("AuthorizeView"))
}

func (uc *UserController) authorizeChat(resp http.ResponseWriter, r *http.Request, user model.User) {
	// r.channel
	resp.Write([]byte("AuthorizeChat"))
}

func (uc *UserController) follow(resp http.ResponseWriter, r *http.Request, user model.User) {
	// r.channel
	resp.Write([]byte("Follow"))
}

func (uc *UserController) unfollow(resp http.ResponseWriter, r *http.Request, user model.User) {
	// r.channel
	resp.Write([]byte("Unfollow"))
}

func (uc *UserController) withPath(path string) string {
	return fmt.Sprintf("%v%v", uc.BasePath, path)
}

func (uc *UserController) GetSessionProvider() api.ISessionProvider {
	return uc.SessionProvider
}

func (uc *UserController) GetBasicRoutes() []api.BasicRoute {
	type route = api.Route
	return []api.BasicRoute{
		{Route: route{Method: api.Get, Path: uc.withPath("/username")}, Handler: uc.getByUsername},
		{Route: route{Method: api.Get, Path: uc.withPath("/token")}, Handler: uc.getByToken},
		{Route: route{Method: api.Delete, Path: uc.withPath("/")}, Handler: uc.removeUser},
	}
}

func (uc *UserController) GetProtectedRoutes() []api.ProtectedRoute {
	type route = api.Route
	return []api.ProtectedRoute{
		{Route: route{Method: api.Get, Path: uc.withPath("/")}, Handler: uc.isAuthenticated},

		{Route: route{Method: api.Get, Path: uc.withPath("/following")}, Handler: uc.getFollowing},
		{Route: route{Method: api.Get, Path: uc.withPath("/is_following")}, Handler: uc.isFollowing},

		{Route: route{Method: api.Get, Path: uc.withPath("/authorize/view")}, Handler: uc.authorizeView},
		{Route: route{Method: api.Get, Path: uc.withPath("/authorize/chat")}, Handler: uc.authorizeChat},

		{Route: route{Method: api.Get, Path: uc.withPath("/follow")}, Handler: uc.follow},
		{Route: route{Method: api.Get, Path: uc.withPath("/unfollow")}, Handler: uc.unfollow},
	}
}
