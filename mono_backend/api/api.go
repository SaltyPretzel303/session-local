package api

import (
	"fmt"
	"net/http"
	"saltypretzel/session-backend/data"
	"strings"

	"github.com/supertokens/supertokens-golang/supertokens"
)

func withCors(next http.Handler) http.Handler {
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

func protected(handler ProtectedHandler) http.Handler {
	return http.HandlerFunc(func(rw http.ResponseWriter, r *http.Request) {
		fmt.Println("protected middleware")

		handler(rw, r, getUser(rw, r))
	})
}

type BasicHandler func(rw http.ResponseWriter, r *http.Request)
type ProtectedHandler func(rw http.ResponseWriter, r *http.Request, user data.User)

func HandleProtected(mux *http.ServeMux, path string, handler ProtectedHandler) {
	mux.Handle(path, withCors(supertokens.Middleware(protected(handler))))
}

func HandleUnprotected(mux *http.ServeMux, path string, handler BasicHandler) {
	mux.Handle(path, withCors(supertokens.Middleware(http.HandlerFunc(handler))))
}

func Listen(mux *http.ServeMux) {
	http.ListenAndServe(":8000", mux)
}
