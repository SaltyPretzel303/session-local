package controllers

import "net/http"

type IController interface {
	GetBasePath() string
	Route(server *http.ServeMux)
}
