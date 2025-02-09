package controllers

import (
	"fmt"
	"net/http"
	"saltypretzel/session-backend/api"
	"saltypretzel/session-backend/model"
)

type KeyController struct {
	// db someDatabase
	Base            string
	SessionProvider api.ISessionProvider
}

func (uc *KeyController) GetBasePath() string {
	return uc.Base
}

func (kc *KeyController) matchKey(resp http.ResponseWriter, r *http.Request) {

}

func (kc *KeyController) generateKey(resp http.ResponseWriter, r *http.Request, user model.User) {

}

func (kc *KeyController) GetSessionProvider() api.ISessionProvider {
	return kc.SessionProvider
}

func (kc *KeyController) withPath(path string) string {
	return fmt.Sprintf("%v%v", kc.Base, path)
}

func (kc *KeyController) GetBasicRoutes() []api.BasicRoute {
	return []api.BasicRoute{
		{Route: api.Route{Method: api.Get, Path: kc.withPath("/match_key")}, Handler: kc.matchKey},
	}
}

func (kc *KeyController) GetProtectedRoutes() []api.ProtectedRoute {
	return []api.ProtectedRoute{
		{Route: api.Route{Method: api.Get, Path: kc.withPath("/get_key")}, Handler: kc.generateKey},
	}
}
