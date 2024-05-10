import { BrowserRouter, Route, Routes } from "react-router-dom";

import Explore from "./Explore";
import { PlayerPage } from "./PlayerPage";
import HeaderBar from "./components/HeaderBar";
import { validUsername } from './Validators'
import { useEffect, useState } from "react";
import { UserInfo } from './Datas'
import config from './Config'

import SuperTokens, { SuperTokensWrapper } from "supertokens-auth-react"
import EmailPassword, { OnHandleEventContext, signOut }
	from 'supertokens-auth-react/recipe/emailpassword'

import Session from 'supertokens-auth-react/recipe/session'

// import Session from 'supertokens-auth-react/recipe/emailpassword'

SuperTokens.init({
	appInfo: {
		appName: "react_app",
		apiDomain: "http://session.com",
		apiBasePath: "/auth",
		websiteDomain: "http://session.com",
		websiteBasePath: "/",
	},
	recipeList: [
		EmailPassword.init({
			onHandleEvent: async (context: OnHandleEventContext) => {
				console.log("Handling post login.")
				console.log(context)

				await new Promise((res) => setTimeout(res, 999))
				// .then((re) => console.log("done waiting 1"))
				// .catch((e) => console.log("Error 1: " + e))
				// .finally(() => console.log("Finaly 1."))

				console.log("Past async call.")
			},
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


export default function Home() {

	const [userInfo, setUserInfo] = useState<UserInfo | undefined>(undefined)
	const [loginVisible, setLoginVisible] = useState(false)
	const [forcedLogin, setForcedLogin] = useState(false)


	// useEffect(() => {
	// 	getUser()
	// }, [userInfo])

	// Not used, callback was broken, async methods would just be ... cancelled
	// without any notice or error.
	async function postLogin(context: OnHandleEventContext) {
		console.log("Handling post login.")

		// if (context.action === "SUCCESS") {
		// 	if (context.isNewRecipeUser && context.user.loginMethods.length === 1) {
		// 		// ^ from documentation 
		// 		console.log("Sig up successfull.")
		// 	} else {
		// 		console.log("Sig in successfull.")
		// 	}

		// 	// await getUser()

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
		console.log("Fetching user from: " + infoUrl)
		try {

			let response = await fetch(infoUrl, { method: 'GET' })

			console.log("Received response.")
			if (response.status != 200) {
				throw Error("Status code: " + response.status)
			}

			let info = await response.json() as UserInfo

			console.log("User info: " + info)
			setUserInfo(info)

			return undefined
		} catch (e) {
			console.log("Error while fetching user data: " + e)
			return undefined
		}

		console.log("Done ith get user.")
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
		<div className='flex flex-col 
			justify-center items-center
			h-dvh w-dvw'>

			<div className='flex h-[50px] min-h-[50px] w-full'>
				<HeaderBar
					loginVisible={loginVisible}
					setLoginVisible={setLoginVisible}
					forcedLogin={forcedLogin}
					loggedIn={userInfo != undefined}
					getUser={getUser}
					logoutHandler={logout} />
			</div>

			<div className='flex size-full 
				justify-center items-center 
				bg-red-500'>

				<SuperTokensWrapper>

					<BrowserRouter>
						<Routes>

							<Route path="/"
								element={<Explore getUser={getUser} />}
							/>

							<Route path="/watch/:channel"
								element={<PlayerPage getUser={getUser} />}
							/>

						</Routes>
					</BrowserRouter>

				</SuperTokensWrapper >
			</div>
		</div>
	)
}