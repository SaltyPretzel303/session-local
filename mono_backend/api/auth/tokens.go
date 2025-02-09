package auth

import (
	"fmt"
	"net/http"
	"saltypretzel/session-backend/config"
	"saltypretzel/session-backend/model"

	"github.com/supertokens/supertokens-golang/recipe/emailpassword"
	"github.com/supertokens/supertokens-golang/recipe/emailpassword/epmodels"
	"github.com/supertokens/supertokens-golang/recipe/session"
	"github.com/supertokens/supertokens-golang/recipe/session/sessmodels"
	"github.com/supertokens/supertokens-golang/supertokens"
)

type IAuthDataProvider interface {
	GetUserByToken(string) (*model.User, error)
}

type TokenSessionProvider struct {
	AuthProvider IAuthDataProvider
}

func (ts TokenSessionProvider) GetSessionUser(w http.ResponseWriter, r *http.Request) *model.User {
	var user *model.User

	// this is hack as fuck
	session.VerifySession(nil, func(rw http.ResponseWriter, r *http.Request) {
		// this handler is gonna be called immediately (.ServeHTTP(w,r) at the end)
		container := session.GetSessionFromRequestContext(r.Context())
		userId := container.GetUserID()

		var err error = nil
		user, err = ts.AuthProvider.GetUserByToken(userId)

		if err != nil {
			user = nil
		}

	}).ServeHTTP(w, r)

	return user
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

func InitSuperTokens(cfg config.Config) error {
	apiBasePath := cfg.Auth.AuthApiBase
	websiteBasePath := cfg.Auth.SiteBasePath

	optionalUsername := false

	cookieDomain := fmt.Sprint(".", cfg.DomainName)

	signInOverride := epmodels.OverrideStruct{
		Functions: func(originalImplementation epmodels.RecipeInterface) epmodels.RecipeInterface {

			extended := extendSignUp(originalImplementation.SignUp)
			originalImplementation.SignUp = &extended

			return originalImplementation
		},
	}

	err := supertokens.Init(supertokens.TypeInput{
		Debug: false,
		Supertokens: &supertokens.ConnectionInfo{
			// ConnectionURI: "http://localhost:3567",
			ConnectionURI: cfg.Auth.TokensCoreAddr,
		},
		AppInfo: supertokens.AppInfo{
			AppName:         cfg.Auth.AppName,
			APIDomain:       cfg.Auth.TokensApiAddr,
			WebsiteDomain:   cfg.DomainName,
			APIBasePath:     &apiBasePath,
			WebsiteBasePath: &websiteBasePath,
		},
		RecipeList: []supertokens.Recipe{
			// emailpassword.Init(nil),
			emailpassword.Init(&epmodels.TypeInput{
				SignUpFeature: &epmodels.TypeInputSignUp{
					FormFields: []epmodels.TypeInputFormField{
						{
							ID:       "usernamer",
							Validate: validateUsername,
							Optional: &optionalUsername,
						},
					},
				},
				Override: &signInOverride,
			}),
			session.Init(&sessmodels.TypeInput{
				CookieDomain: &cookieDomain,
			}),
		},
	})

	if err != nil {
		return err
	}

	return nil
}

func listTokens() []string {
	pageCnt := 100
	recipes := []string{"emailpassword"}

	tokens := []string{}

	dmy := "" // dummy value for first interation
	var pageToken *string = &dmy

	for pageToken != nil {
		res, err := supertokens.GetUsersNewestFirst("", pageToken, &pageCnt, &recipes, nil)

		if err != nil {
			for _, single := range res.Users {
				tokens = append(tokens, single.User["id"].(string))
			}
		}

		pageToken = res.NextPaginationToken
	}

	return tokens
}

func removeToken(token string) error {
	return supertokens.DeleteUser(token)
}

func (sp *TokenSessionProvider) MergeUsers(dProvider IAuthDataProvider) {
	tokens := listTokens()
	fmt.Println("merging tokens: ", tokens)

	for _, token := range tokens {
		if user, _ := dProvider.GetUserByToken(token); user != nil {

			fmt.Println("removing token: ", token)
			err := removeToken(token)

			if err != nil {
				fmt.Println("failed to remove token: ", token)
			}
		}
	}

}
