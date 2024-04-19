import { BrowserRouter, Route, Router, Routes } from "react-router-dom";
import SuperTokens from "supertokens-auth-react";
import EmailPassword, { OnHandleEventContext } from 'supertokens-auth-react/recipe/emailpassword'
import { SessionAuth } from "supertokens-auth-react/recipe/session";
import Session from 'supertokens-auth-react/recipe/session'
// import Session from 'supertokens-auth-react/recipe/emailpassword'
import { signOut } from "supertokens-auth-react/recipe/emailpassword"

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
import RecipeEventWithSessionContext from "supertokens-auth-react/recipe/session";
// "supertokens-auth-react/recipe/session/types";

export default function Home() {

	const [userInfo, setUserInfo] = useState<UserInfo | undefined>(undefined)
	const [loginVisible, setLoginVisible] = useState(false)
	const [forcedLogin, setForcedLogin] = useState(false)

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
					// If multi domain is set on the backend, this field MUST
					// have the same value as cookie_domain in session.init()

					// sessionTokenBackendDomain: ".session.com"
					// ^ Not documented for emailpassword login, avoid.
				}
			)

		]
	});

	// signOut()
	// 	.then(() => {
	// 		console.log("Signout done")
	// 	})
	// 	.catch((err) => {
	// 		console.log("Failed to signout: " + err)
	// 	})

	async function postLogin(context: OnHandleEventContext) {
		if (context.action === "SUCCESS") {
			if (context.isNewRecipeUser && context.user.loginMethods.length === 1) {
				// ^ from documentation 
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

	async function getUser(): Promise<UserInfo | undefined> {
		if (userInfo != undefined) {
			console.log("User data already fetched, returning.")
			return userInfo
		}

		if (! await Session.doesSessionExist()) {
			console.log("Session doesn't exits.")
			return undefined
		}

		console.log("Session exists, will try to fetch user.")

		let userTokensId = await Session.getUserId()

		let infoUrl = config.userFromTokensIdUrl(userTokensId)
		let response = await fetch(infoUrl, { method: 'GET' })

		if (response.status != 200) {
			console.log("Return status: " + response.status
				+ " msg: " + await response.text())
			return undefined
		}

		let info = await response.json() as UserInfo

		setUserInfo(info)

		return info
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

		// root
		<div className='flex flex-col h-screen w-screen'>

			<div className='h-14 w-full'>
				<HeaderBar
					loginVisible={loginVisible}
					setLoginVisible={setLoginVisible}
					forcedLogin={forcedLogin}
					loggedIn={userInfo != undefined}
					getUser={getUser}
					logoutHandler={logout} />
			</div>

			<div className='h-full w-full'>
				<SuperTokensWrapper>

					<BrowserRouter>
						<Routes>

							<Route path="/"
								element={
									<Explore
										getUser={getUser} />
								}
							/>

							<Route path="/watch/:channel"
								element={
									<PlayerPage
										// user={userInfo}
										getUser={getUser}
									// getUser is redundant and only used 
									// so that it can be navigated back to / <- home
									/>
								}
							/>

							// mockups
							<Route path="/play" element={<QuickPlay />} />
							<Route path="/do" element={<DoFetch />} />
						</Routes>
					</BrowserRouter>

				</SuperTokensWrapper >
			</div>
		</div>
	)
}