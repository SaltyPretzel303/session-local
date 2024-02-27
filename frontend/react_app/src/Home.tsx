import { BrowserRouter, Route, Router, Routes } from "react-router-dom";
import SuperTokens from "supertokens-auth-react";
import ThirdPartyEmailPassword, { Github, Google } from "supertokens-auth-react/recipe/thirdpartyemailpassword";
import EmailPassword from 'supertokens-auth-react/recipe/emailpassword'
import Session from "supertokens-auth-react/recipe/session";
import './style/Home.css'

import { SuperTokensWrapper } from "supertokens-auth-react";
import Explore from "./Explore";
import { PlayerPage } from "./PlayerPage";
import HeaderBar from "./components/HeaderBar";
import QuickPlay from "./QuickPlay";
import { validUsername } from './Validators'

export default function Home() {

	SuperTokens.init({
		appInfo: {
			appName: "react_app",
			apiDomain: "http://session.com",
			apiBasePath: "/auth",
			// websiteDomain: "http://session.com:3000"
			websiteDomain: "http://session.com",
			websiteBasePath: "/"
		},
		recipeList: [
			EmailPassword.init({
				signInAndUpFeature: {
					signUpForm: {
						formFields: [
							{
								id: "username",
								label: "Unique Username",
								validate: validUsername
							}
						]
					}
				}
			}),
			Session.init(
				{
					sessionTokenBackendDomain: ".session.com"
					// If multi domain is set on the backend, this field MUST
					// have the same value as cookie_domain in session.init()
				}
			)

		]
	});

	return (

		<SuperTokensWrapper>

			<HeaderBar />

			<BrowserRouter>
				<Routes>
					<Route path="/" element={<Explore />} />
					<Route path="/watch:streamer" element={<PlayerPage user={null} />} />
					<Route path="/play" element={<QuickPlay />} />
				</Routes>
			</BrowserRouter>

		</SuperTokensWrapper >

	)
}