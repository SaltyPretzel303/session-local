import { BrowserRouter, Route, Routes } from "react-router-dom";

import Explore from "./Explore";
import { PlayerPage } from "./PlayerPage";
import HeaderBar from "./components/HeaderBar";
import { validUsername } from './Validators'
import { useEffect, useState } from "react";
import { StreamInfo, UserInfo } from './Datas'
import config from './Config'

import SuperTokens, { SuperTokensWrapper } from "supertokens-auth-react"
import EmailPassword, { OnHandleEventContext, signOut }
	from 'supertokens-auth-react/recipe/emailpassword'

import Session, { validateClaims } from 'supertokens-auth-react/recipe/session'

// SuperTokens.init({
// 	appInfo: {
// 		appName: "SessionApp",
// 		apiDomain: `http://${config.domainName}`,
// 		apiBasePath: "/auth",
// 		websiteDomain: `http://${config.domainName}`,
// 		websiteBasePath: "/",
// 	},
// 	recipeList: [
// 		EmailPassword.init({
// 			onHandleEvent: (context: OnHandleEventContext) => {
// 				console.log("Handling post login.")

// 				if (context.action === "SUCCESS") {
// 					if (context.isNewRecipeUser && context.user.loginMethods.length === 1) {
// 						console.log("Sig up successfull.")
// 					} else {
// 						console.log("Sig in successfull.")
// 					}

// 					// await loadUser()
// 				}

// 				// Two ways to check does session exists.
// 				// 	if(!context.loading && context.doesSessionExist){
// 				// 		^ this one allowed only inside < SupertokensWrapper(or context ... ?) >
// 				// }
// 				// if (await Session.doesSessionExist()) {

// 			},
// 			signInAndUpFeature: {
// 				signUpForm: {
// 					formFields: [
// 						{
// 							id: "username",
// 							label: "Unique Username",
// 							validate: validUsername
// 						}
// 					]
// 				}
// 			}
// 		}),
// 		Session.init(
// 			{
// 				sessionTokenFrontendDomain: `.${config.domainName}`,
// 				// If multi domain is set on the backend, this field MUST
// 				// have the same value as cookie_domain in session.init()

// 				// sessionTokenBackendDomain: ".session.com"
// 				// ^ Not documented for emailpassword login, AVOID.
// 			}
// 		)

// 	]
// });

export default function Home() {

	const [userInfo, setUserInfo] = useState<UserInfo | undefined>(undefined)
	const [streamInfo, setStreamInfo] = useState<StreamInfo | undefined>(undefined)

	const [loginVisible, setLoginVisible] = useState(false)
	const [forcedLogin, setForcedLogin] = useState(false)

	useEffect(() => {
		console.log("Setting up tokens.")

		SuperTokens.init({
			appInfo: {
				appName: "SessionApp",
				apiDomain: `http://${config.domainName}`,
				apiBasePath: "/auth",
				websiteDomain: `http://${config.domainName}`,
				websiteBasePath: "/",
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
						sessionTokenFrontendDomain: `.${config.domainName}`,
						// If multi domain is set on the backend, this field MUST
						// have the same value as cookie_domain in session.init()

						// sessionTokenBackendDomain: ".session.com"
						// ^ Not documented for emailpassword login, AVOID.
					}
				)

			]
		});
	}, [])


	async function postLogin(context: OnHandleEventContext) {
		console.log("Handling post login.")

		if (context.action === "SUCCESS") {
			if (context.isNewRecipeUser && context.user.loginMethods.length === 1) {
				console.log("Sig up successfull.")
			} else {
				console.log("Sig in successfull.")
			}

			await loadUser()
		}

		// Two ways to check does session exists.
		// 	if(!context.loading && context.doesSessionExist){
		// 		^ this one allowed only inside < SupertokensWrapper(or context ... ?) >
		// }
		// if (await Session.doesSessionExist()) {

	}

	async function loadUser(): Promise<UserInfo | undefined> {
		if (userInfo != undefined) {
			console.log("User data already fetched, returning.")
			return userInfo
		}

		if (! await Session.doesSessionExist()) {
			console.log("Session does not exist, won't fetch user data.")
			return undefined
		}

		console.log("Session exists, will try to fetch user.")

		let userTokensId = await Session.getUserId()
		let infoUrl = config.userFromTokensIdUrl(userTokensId)

		try {
			let response = await fetch(infoUrl, { method: 'GET' })

			if (response.status != 200) {
				throw Error("Status code: " + response.status)
			}

			let info = await response.json() as UserInfo

			console.log("Fetched user: " + JSON.stringify(info))

			setUserInfo(info)

			return info
		} catch (e) {
			console.log("Error while fetching user data: " + e)
			setUserInfo(undefined)
			return undefined
		}
	}

	async function loadStream(): Promise<StreamInfo | undefined> {
		if (userInfo == undefined) {
			console.log("User not found, can't load stream info.")
			return
		}

		try {
			let url = config.streamInfoUrl(userInfo.username, config.myRegion)
			let res = await fetch(url)

			if (res.status != 200) {
				throw Error("status code: " + res.status)
			}

			let data = await res.json() as StreamInfo

			console.log("Stream info: " + JSON.stringify(data))
			setStreamInfo(data)

			return data
		} catch (e) {
			console.log("Failed to load stream info: " + e)
			setStreamInfo(undefined)
			return undefined
		}
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
		// <SuperTokensWrapper>
		<div>
			<HeaderBar
				loginVisible={loginVisible}
				setLoginVisible={setLoginVisible}
				forcedLogin={forcedLogin}
				user={userInfo}
				getUser={loadUser}
				stream={streamInfo}
				getStream={loadStream}
				logoutHandler={logout} />

			<button onClick={async () => {
				console.log("Will validate someone")
				let res = await fetch("http://session.com/api/v1/user/username?username=someone")
				// let res = await fetch("http://localhost:3000/api/v1/user/username?username=someone")
				// let res = await fetch("http://localhost:3000/api/v1/user/token?token=some_token")
				console.log(`valid username: ${res}`)

			}}>CLICK ON ME</button>
		</div>
		// </SuperTokensWrapper>

		// <div className='flex flex-col 
		// 	justify-center items-center
		// 	overflow-hidden
		// 	h-dvh w-dvw'>

		// 	<SuperTokensWrapper>

		// 		<BrowserRouter>

		// 			<div className='flex h-[50px] min-h-[50px] w-full'>
		// 				<HeaderBar
		// 					loginVisible={loginVisible}
		// 					setLoginVisible={setLoginVisible}
		// 					forcedLogin={forcedLogin}
		// 					user={userInfo}
		// 					getUser={loadUser}
		// 					stream={streamInfo}
		// 					getStream={loadStream}
		// 					logoutHandler={logout} />
		// 			</div>

		// 			<div className='flex size-full 
		// 						justify-center items-center 
		// 						overflow-hidden
		// 						bg-white'>
		// 				<Routes>

		// 					<Route path="/" element={
		// 						<div>
		// 							EMPTY
		// 						</div>
		// 					} />

		// 					{/* <Route path="/"
		// 						element={<Explore getUser={loadUser} />}
		// 					/>

		// 					<Route path="/watch/:channel"
		// 						element={<PlayerPage getUser={loadUser} />}
		// 					/> */}

		// 				</Routes>

		// 			</div>

		// 		</BrowserRouter>

		// 	</SuperTokensWrapper >
		// </div>
	)
}