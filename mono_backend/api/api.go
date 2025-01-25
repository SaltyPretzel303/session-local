package api

import (
	"fmt"
	"net/http"
	"saltypretzel/session-backend/api/auth"
	"saltypretzel/session-backend/model"
	"strings"

	"github.com/supertokens/supertokens-golang/supertokens"
)

func WithCors(next http.Handler) http.Handler {
	return http.HandlerFunc(func(response http.ResponseWriter, r *http.Request) {
		fmt.Println("cors midleware")
		response.Header().Set("Access-Control-Allow-Origin", "http://localhost:3000")
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

func WithUser(sProvider auth.ISessionProvider, handler ProtectedHandler) http.Handler {

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

func HandleProtected(mux *http.ServeMux,
	path string,
	sProvider auth.ISessionProvider,
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
