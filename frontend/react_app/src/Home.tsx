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

import Session from 'supertokens-auth-react/recipe/session'

SuperTokens.init({
	appInfo: {
		appName: "react_app",
		apiDomain: `http://${config.domainName}`,
		apiBasePath: "/auth",
		websiteDomain: `http://${config.domainName}`,
		websiteBasePath: "/",
	},
	recipeList: [
		EmailPassword.init({
			onHandleEvent: async (context: OnHandleEventContext) => {
				console.log("Handling post login.")
				console.log(context)

				await new Promise((res) => setTimeout(res, 1000))

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
				sessionTokenFrontendDomain: `.${config.domainName}`,
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
	const [streamInfo, setStreamInfo] = useState<StreamInfo | undefined>(undefined)

	const [loginVisible, setLoginVisible] = useState(false)
	const [forcedLogin, setForcedLogin] = useState(false)

	// useEffect(() => {
	// 	loadInfo()
	// }, [userInfo, streamInfo])

	// async function loadInfo() {
	// 	if (userInfo != undefined) {
	// 		console.log("User already fetched in home.")
	// 		return
	// 	}

	// 	console.log("Will load user in home.")
	// 	let user = await loadUser() // will call setUserInfo

	// 	if (user == undefined) {
	// 		console.log("User undefined, wont load stream info.")
	// 		return
	// 	}

	// 	console.log("Will load stream in home.")
	// 	let stream = await loadStream() // will call setStreamInfo
	// }

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

	async function loadUser(): Promise<UserInfo | undefined> {
		if (userInfo != undefined) {
			console.log("User data already fetched, returning.")
			return userInfo
		}

		if (! await Session.doesSessionExist()) {
			console.log("Session does not exist.")
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

		<div className='flex flex-col 
			justify-center items-center
			overflow-hidden
			h-dvh w-dvw'>

			<SuperTokensWrapper>

				<BrowserRouter>
					<div className='flex h-[50px] min-h-[50px] w-full'>
						<HeaderBar
							loginVisible={loginVisible}
							setLoginVisible={setLoginVisible}
							forcedLogin={forcedLogin}
							user={userInfo}
							getUser={loadUser}
							stream={streamInfo}
							getStream={loadStream}
							logoutHandler={logout} />
					</div>

					<div className='flex size-full 
								justify-center items-center 
								overflow-hidden
								bg-white'>
						<Routes>

							<Route path="/"
								element={<Explore getUser={loadUser} />}
							/>

							<Route path="/watch/:channel"
								element={<PlayerPage getUser={loadUser} />}
							/>

						</Routes>

					</div>
					
				</BrowserRouter>

			</SuperTokensWrapper >
		</div>
	)
}