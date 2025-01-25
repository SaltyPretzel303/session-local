package auth

import (
	"fmt"
	"net/http"
	"saltypretzel/session-backend/api/services"
	"saltypretzel/session-backend/db"
	"saltypretzel/session-backend/model"

	"github.com/supertokens/supertokens-golang/recipe/emailpassword"
	"github.com/supertokens/supertokens-golang/recipe/emailpassword/epmodels"
	"github.com/supertokens/supertokens-golang/recipe/session"
	"github.com/supertokens/supertokens-golang/recipe/session/sessmodels"
	"github.com/supertokens/supertokens-golang/supertokens"
)

type ISessionProvider interface {
	GetSessionUser(w http.ResponseWriter, r *http.Request) *model.User
}

type TokenSessionProvider struct {
	UserService services.UserService
}

func (ts TokenSessionProvider) GetSessionUser(w http.ResponseWriter, r *http.Request) *model.User {
	var user *db.User

	// this is hack as fuck
	session.VerifySession(nil, func(rw http.ResponseWriter, r *http.Request) {
		// this handler is gonna be called immediately (.ServeHTTP(w,r))
		container := session.GetSessionFromRequestContext(r.Context())
		userId := container.GetUserID()

		var err error = nil
		user, err = ts.UserService.GetUserByToken(userId)

		if err != nil {
			user = nil
		}

	}).ServeHTTP(w, r)

	if user != nil {
		return user.AsModel()
	} else {
		return nil
	}
}

func validateUsername(value interface{}, tenantId string) *string {
	asStr := value.(string)
	return &asStr
}

type signUpFunction = func(email string,
	password string,
	tenantId string,
	userContext supertokens.UserContext) (epmodels.SignUpResponse, error)

func extendSignUp(original *signUpFunction) signUpFunction {
	return func(email string,
		password string,
		tenantId string,
		userContext supertokens.UserContext) (epmodels.SignUpResponse, error) {

		fmt.Println("Doing extended signup processing.")

		// TODO somehow get a username and do a validation.
		// Continue if unique.

		_, err := (*original)(email, password, tenantId, userContext)

		if err != nil {
			return epmodels.SignUpResponse{}, nil
		}

		return epmodels.SignUpResponse{OK: &struct{ User epmodels.User }{User: epmodels.User{}}}, nil
	}
}

// TODO refactor to take config ?
func InitSetupTokens() error {
	apiBasePath := "/auth"
	websiteBasePath := "/"

	// optionalUsername := false

	cookieDomain := ".session.com"

	// signInOverride := epmodels.OverrideStruct{
	// 	Functions: func(originalImplementation epmodels.RecipeInterface) epmodels.RecipeInterface {

	// 		extended := extendSignUp(originalImplementation.SignUp)
	// 		originalImplementation.SignUp = &extended

	// 		return originalImplementation
	// 	},
	// }

	err := supertokens.Init(supertokens.TypeInput{
		Debug: true,
		Supertokens: &supertokens.ConnectionInfo{
			// ConnectionURI: "http://tokens-core:3567",
			ConnectionURI: "http://localhost:3567",
		},
		AppInfo: supertokens.AppInfo{
			AppName: "react_app",
			// APIDomain:       "http://tokens-api.session.com",
			APIDomain:       "http://session.com:8000",
			WebsiteDomain:   "http://session.com",
			APIBasePath:     &apiBasePath,
			WebsiteBasePath: &websiteBasePath,
		},
		RecipeList: []supertokens.Recipe{
			emailpassword.Init(nil),
			// emailpassword.Init(&epmodels.TypeInput{
			// 	SignUpFeature: &epmodels.TypeInputSignUp{
			// 		FormFields: []epmodels.TypeInputFormField{
			// 			{
			// 				ID:       "usernamer",
			// 				Validate: validateUsername,
			// 				Optional: &optionalUsername,
			// 			},
			// 		},
			// 	},
			// 	Override: &signInOverride,
			// }),
			session.Init(&sessmodels.TypeInput{
				CookieDomain: &cookieDomain,
			}),
		},
	})

	if err != nil {
		fmt.Printf("error initializing supertokens: %v \n", err)
		return err
	}

	return nil
}
