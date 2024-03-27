import { BrowserRouter, Route, Router, Routes } from "react-router-dom";
import SuperTokens from "supertokens-auth-react";
import ThirdPartyEmailPassword, { Github, Google } from "supertokens-auth-react/recipe/thirdpartyemailpassword";
import EmailPassword, { OnHandleEventContext } from 'supertokens-auth-react/recipe/emailpassword'
import Session, { SessionAuth, signOut } from "supertokens-auth-react/recipe/session";
// import './style/Home.css'

import { SuperTokensWrapper } from "supertokens-auth-react";
import Explore from "./Explore";
import { PlayerPage } from "./PlayerPage";
import HeaderBar from "./components/HeaderBar";
import QuickPlay from "./QuickPlay";
import { validUsername } from './Validators'
import { useEffect, useState } from "react";
import { UserInfo } from './Datas'
import config from './Config'
import DoFetch from "./components/DoFetch";

export default function Home() {

	const [userInfo, setUserInfo] = useState<UserInfo | undefined>(undefined)

	SuperTokens.init({
		appInfo: {
			appName: "react_app",
			apiDomain: "http://session.com",
			apiBasePath: "/auth",
			websiteDomain: "http://session.com",
			websiteBasePath: "/"
		},
		recipeList: [
			EmailPassword.init({
				onHandleEvent: postLogin,
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
					sessionTokenFrontendDomain: ".session.com",
					// sessionTokenBackendDomain: ".session.com"
					// If multi domain is set on the backend, this field MUST
					// have the same value as cookie_domain in session.init()
				}
			)

		]
	});


	async function postLogin(context: OnHandleEventContext) {
		if (context.action === "SUCCESS") {
			if (context.isNewRecipeUser && context.user.loginMethods.length === 1) {
				console.log("Sig in/up successfull.")
				getUser()
			}
		}
	}

	// Two ways to check does session exists.
	// if (!context.loading && context.doesSessionExist){
	// 		^ this one allowed only inside <SupertokensWrapper (or context ... ?)>
	// }
	// if (await Session.doesSessionExist()){

	// }

	// maybe move this in to the config (already moved, just use it)
	async function getUser(): Promise<UserInfo | undefined> {
		if (userInfo != undefined) {
			console.log("User data already fetched, returning.")
			return userInfo
		}

		if (! await Session.doesSessionExist()) {
			console.log("Session doesn't exits.")
			return undefined
		}

		console.log("Session exits, will try to fetch user.")

		let userTokensId = await Session.getUserId()
		let infoUrl = config.userFromTokensIdUrl(userTokensId)

		let response = await fetch(infoUrl, { method: 'GET' })

		if (response.status != 200) {
			console.log("Return status not 200: " + await response.text)
			return undefined
		}

		setUserInfo(await response.json() as UserInfo)

		// return await response.json() as UserInfo 
		// ^^ Will have the same effect just with the type annotation.
		return userInfo
	}

	async function logout() {
		if (!Session.doesSessionExist()) {
			console.log("No active session.")
			return
		}

		console.log("Will perform signout.")
		await signOut()
		console.log("Signout done.")
		
		setUserInfo(undefined)
	}

	return (

		<SuperTokensWrapper>

			<HeaderBar
				loggedIn={userInfo != undefined}
				userProvider={getUser}
				logoutHandler={logout} />

			<BrowserRouter>
				<Routes>
					<Route path="/"
						element={
							<Explore
								getUser={getUser} />
						}
					/>

					<Route path="/watch/:streamer"
						element={
							<PlayerPage
								getUser={getUser}
							// streamData={undefined} 
							/>
						}
					/>

					<Route path="/play" element={<QuickPlay />} />
					<Route path="/do" element={<DoFetch />} />
				</Routes>
			</BrowserRouter>

		</SuperTokensWrapper >

	)
}