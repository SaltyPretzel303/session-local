package controllers

import (
	"encoding/json"
	"net/http"
	"saltypretzel/session-backend/api"
	"saltypretzel/session-backend/api/auth"
	"saltypretzel/session-backend/api/services"
	"saltypretzel/session-backend/model"
)

const (
	KEY_ARG = "req_key"
)

type UserController struct {
	BasePath        string
	UserService     *services.UserService
	SessionProvider auth.ISessionProvider
}

func (uc *UserController) GetBasePath() string {
	return uc.BasePath
}

func (uc *UserController) getByUsername(resp http.ResponseWriter, r *http.Request) {
	username := r.Form.Get("username")
	user, err := uc.UserService.GetUserByUsername(username)

	if err != nil {
		resp.Write([]byte("Error"))
		return
	}
	rData, err := json.Marshal(user)
	if err != nil {
		resp.Write([]byte("Error"))
		return
	}

	resp.Write([]byte(rData))
}

func (uc *UserController) getByToken(resp http.ResponseWriter, r *http.Request) {
	// r.tokensid
	resp.Write([]byte("GetUserByToken"))
}

func (uc *UserController) isAuthenticated(resp http.ResponseWriter, r *http.Request, user model.User) {
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

// TODO refactor so this is in generator method
func (uc *UserController) Route(server *http.ServeMux) {
	api.HandleUnprotected(server, GET(uc, "/username"), uc.getByUsername)
	api.HandleUnprotected(server, GET(uc, "/token"), uc.getByToken)

	// TODO revisit this one, this may be a path conflict
	api.HandleProtected(server, GET(uc, "/"), uc.SessionProvider, uc.isAuthenticated)

	api.HandleProtected(server, GET(uc, "/following"), uc.SessionProvider, uc.getFollowing)
	api.HandleProtected(server, GET(uc, "/is_following"), uc.SessionProvider, uc.isFollowing)

	// TODO add admin role, also user should be able to remove itself
	// testing purpose only !!!
	api.HandleUnprotected(server, DELETE(uc, "/"), uc.removeUser)

	// TODO move to channel.controller
	api.HandleProtected(server, GET(uc, "/authorize/view"), uc.SessionProvider, uc.authorizeView)
	api.HandleProtected(server, GET(uc, "/authorize/chat"), uc.SessionProvider, uc.authorizeChat)

	api.HandleProtected(server, GET(uc, "/follow"), uc.SessionProvider, uc.follow)
	api.HandleProtected(server, GET(uc, "/unfollow"), uc.SessionProvider, uc.unfollow)

}
