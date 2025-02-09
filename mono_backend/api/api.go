package api

import (
	"fmt"
	"net/http"
	"saltypretzel/session-backend/model"
	"strings"

	"github.com/supertokens/supertokens-golang/supertokens"
)

type ISessionProvider interface {
	GetSessionUser(w http.ResponseWriter, r *http.Request) *model.User
}

func WithCors(next http.Handler) http.Handler {
	return http.HandlerFunc(func(response http.ResponseWriter, r *http.Request) {
		response.Header().Set("Access-Control-Allow-Origin", "http://session.com")
		response.Header().Set("Access-Control-Allow-Credentials", "true")

		if r.Method == "OPTIONS" {
			// TODO extract this in auth package
			tokensHeaders := supertokens.GetAllCORSHeaders()
			headers := strings.Join(append([]string{"Content-Type"}, tokensHeaders...), ", ")
			response.Header().Set("Access-Control-Allow-Headers", headers)

			response.Header().Set("Access-Control-Allow-Methods", "*")
			response.Write([]byte(""))
		} else {
			next.ServeHTTP(response, r)
		}

	})
}

func WithUser(sProvider ISessionProvider, handler ProtectedHandler) http.Handler {
	return http.HandlerFunc(func(rw http.ResponseWriter, r *http.Request) {
		fmt.Println("protected middleware")

		user := sProvider.GetSessionUser(rw, r)

		if user == nil {
			rw.WriteHeader(http.StatusUnauthorized)
			return
		}

		handler(rw, r, *user)
	})
}

type BasicHandler func(rw http.ResponseWriter, r *http.Request)
type ProtectedHandler func(rw http.ResponseWriter, r *http.Request, user model.User)

func HandleProtected(mux *http.ServeMux, path string, sProvider ISessionProvider,
	handler ProtectedHandler) {

	mux.Handle(path, WithUser(sProvider, handler))
}

func HandleUnprotected(mux *http.ServeMux, path string, handler BasicHandler) {
	mux.Handle(path, http.HandlerFunc(handler))
}

type Middleware func(http.Handler) http.Handler

func WithMiddleware(mux *http.ServeMux, handlers ...Middleware) http.Handler {
	var asHandler http.Handler = mux
	for _, handler := range handlers {
		asHandler = handler(asHandler)
	}
	return asHandler
}

type Method string

const (
	Get    Method = "GET"
	Post   Method = "POST"
	Delete Method = "DELETE"
)

type Route struct {
	Method Method
	Path   string
}

func (r Route) FormPath(prefix string) string {
	return fmt.Sprintf("%v %v%v", r.Method, prefix, r.Path)
}

type BasicRoute struct {
	Route
	Handler BasicHandler
}

type ProtectedRoute struct {
	Route
	Handler ProtectedHandler
}

type IController interface {
	GetBasicRoutes() []BasicRoute
	GetProtectedRoutes() []ProtectedRoute
}

type IProtectedController interface {
	GetSessionProvider() ISessionProvider
}

func Apply(mux *http.ServeMux, base string, controller IController) {
	routes := controller.GetBasicRoutes()
	fmt.Println("Applying basic routes: ")
	for _, route := range routes {
		path := route.FormPath(base)

		fmt.Println("Applying route: ", path)
		mux.Handle(path, http.HandlerFunc(route.Handler))
	}

	pRoutes := controller.GetProtectedRoutes()

	if asProtected, ok := controller.(IProtectedController); ok {
		fmt.Println("Applying protected routes: ")
		sProvider := asProtected.GetSessionProvider()

		for _, route := range pRoutes {
			path := route.FormPath(base)

			fmt.Println("Applying route: ", path)
			mux.Handle(path, WithUser(sProvider, route.Handler))
		}
	} else if len(pRoutes) > 0 {
		fmt.Println("Controller contains protected routes but can't provide session provider.")
		fmt.Println(controller)
	}

}
