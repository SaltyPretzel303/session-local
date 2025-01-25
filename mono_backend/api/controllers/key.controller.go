package controllers

import (
	"net/http"
	"saltypretzel/session-backend/api"
	"saltypretzel/session-backend/api/auth"
	"saltypretzel/session-backend/model"
)

type KeyController struct {
	// db someDatabase
	base            string
	SessionProvider auth.ISessionProvider
}

func (uc *KeyController) GetBasePath() string {
	return uc.base
}

func (kc *KeyController) matchKey(resp http.ResponseWriter, r *http.Request) {

}

func (kc *KeyController) generateKey(resp http.ResponseWriter,
	r *http.Request,
	user model.User) {

}

func (kc *KeyController) Route(server *http.ServeMux) {
	api.HandleUnprotected(server, GET(kc, "/key/match"), kc.matchKey)
	api.HandleProtected(server, GET(kc, "/key"), kc.SessionProvider, kc.generateKey)
}
