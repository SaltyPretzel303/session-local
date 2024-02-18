import { useEffect, Dispatch, useState } from "react";
import Modal from "react-modal";
import Overlay from 'react-modal'
import { signUp } from "supertokens-auth-react/lib/build/recipe/emailpassword";
import { SignInAndUp } from "supertokens-auth-react/recipe/thirdpartyemailpassword/prebuiltui"
import config from '../Config'

type LoginPopupProps = {
	loginVisible: boolean
	setLoginVisible: Dispatch<boolean>
}

type FormState = {
	name: string,
	question: string,
	switchButtonTxt: string,
	mainButtonTxt: string,
	usernameHidden: boolean,
	repeatPasswordHidden: boolean,
	// mainButtonClickHandler: () => void
}

export default function LoginPopup(props: LoginPopupProps) {


	const signInStateName = "signIn"
	const signUpStateName = "signUp"

	const signInState: FormState = {
		name: signInStateName,
		question: "Don't have an account?\t",
		switchButtonTxt: "SignUp",
		mainButtonTxt: "SignIn",
		usernameHidden: true,
		repeatPasswordHidden: true,
		// mainButtonClickHandler: signInClickHandler
	}

	const signUpState: FormState = {
		name: signUpStateName,
		question: "Already have an account? ",
		switchButtonTxt: "SignIn",
		mainButtonTxt: "SignUp",
		usernameHidden: false,
		repeatPasswordHidden: false,
		// mainButtonClickHandler: signUpClickHandler
	}

	const [formState, setFormState] = useState(signInState)

	const [email, setEmail] = useState("")
	const [username, setUsername] = useState("")
	const [password, setPassword] = useState("")
	const [repPassword, setRepPassword] = useState("")
	const [pwdNotMatching, setPwdNotMatching] = useState(false)


	function switchInUp() {
		console.log("Switching state")

		if (formState.name == signInStateName) {
			setFormState(signUpState)
			console.log("Switching to UP state.")
		} else {
			setFormState(signInState)
			console.log("Switching to IN state")
		}
	}

	const decorated = {
		background: "none",
		border: "none",
		color: "darkblue",
		// fontSize: "22px"
	}

	const regular = {
		background: "none",
		border: "none",
		color: "orange",
		// fontSize: "20px"
	}

	const [swBtnDecoration, setSwBtnDecoration] = useState(regular)

	function VerticalSpacer() {
		return (
			<div style={{ height: "20px" }}></div>
		)
	}

	function HorizontalSpacer() {
		return (
			<div style={{ width: "20px" }}></div>
		)
	}

	function NotMatchingPasswordError() {
		return <div style={{ color: "red" }}>Password not matching!</div>
	}


	function repeatPasswordWatcher(e: React.ChangeEvent<HTMLInputElement>) {
		let newRpwd = e.target.value
		setRepPassword(newRpwd)

		if (password == "" || password != newRpwd) {
			setPwdNotMatching(true)
		} else {
			setPwdNotMatching(false)
		}

	}


	function mainButtonClick() {
		if (formState.name == signInStateName) {
			signInClickHandler()
		} else {
			signUpClickHandler()
		}
	}

	function collectData() {
		return {
			formFields: [
				{
					id: "email",
					value: email
				},
				{
					id: "password",
					value: password
				}
			]
		}
	}

	function signInClickHandler() {
		console.log("Handling singin button click ...")
	}

	function signUpClickHandler() {
		console.log("Handling signup button click ...")

		if (pwdNotMatching) {
			console.log("Passwords are not matching.")
			return
		}

		let data = collectData()
		console.log(JSON.stringify(data))

		fetch(config.signUpUrl,
			{
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(data)
			})
			.then((res: Response) => {
				if (res.status != 200) {
					console.log("SignUp request failed with: " + res.status)
					return
				}
				console.log("SignUp request successfull.")

			})
			.catch((err) => {
				console.log("Error with signup request: " + err)
			})
	}

	return (
		<div>

			<Overlay
				style={{
					// overlay: {
					// 	display: "flex",
					// 	flexDirection: "row",
					// 	justifyContent: "center",
					// 	alignContent: "center"
					// },
					content: {
						// width: "500px",
						// border: "2px solid black",
						// display: "flex",
						// flexDirection: "column"
					}
				}}
				ariaHideApp={false}
				isOpen={props.loginVisible}
				shouldCloseOnEsc={true}
				onRequestClose={() => props.setLoginVisible(false)}>

				{/* <Modal
					ariaHideApp={false}
					isOpen={props.loginVisible}
					contentLabel="Auth Modal"
					shouldCloseOnEsc={true}
					onRequestClose={() => props.setLoginVisible(false)}> */}

				<SignInAndUp redirectOnSessionExists={false} />

				{/* Main container */}
				{false && <div style={{
					display: "flex",
					justifyContent: "center",
					alignContent: "center",
					// border: "2px dashed darkgreen",
					width: "100%",
					height: "100%"
				}}>
					<div style={
						{
							border: "4px solid orange",
							padding: "20px",
							width: "20%",
							height: "60%",
							display: "flex",
							flexDirection: "column",
							justifyContent: "center",
							alignContent: "center",
							// textAlign: "center"
						}
					}>

						{/* Title */}
						<h1 style={{ textAlign: "center" }}>Session</h1>

						{/* Question container */}
						<div style={
							{
								display: "flex",
								flexDirection: "row",
								justifyContent: "center"
							}
						}>
							<div>{formState.question} </div>
							<HorizontalSpacer />
							<button
								style={swBtnDecoration}
								onClick={switchInUp}
								onMouseEnter={() => setSwBtnDecoration(decorated)}
								onMouseLeave={() => setSwBtnDecoration(regular)}

							>{formState.switchButtonTxt}</button>
						</div>

						<hr style={{ width: "80%" }} />

						{/* Email input */}
						<label>Email</label>
						<input type="text"
							placeholder="Email"
							onChange={(e) => setEmail(e.target.value)} />

						{/* Username input */}
						{!formState.usernameHidden &&
							<div
								style={{ display: "flex", flexDirection: "column" }}>
								<VerticalSpacer />
								<label>Username</label>
								<input type="text"
									placeholder="Usernamer"
									onChange={(e) => setUsername(e.target.value)} />
							</div>
						}

						<VerticalSpacer />

						{/* Password input */}
						<label>Password</label>
						<input type="password"
							placeholder="Password"
							onChange={(e) => setPassword(e.target.value)} />

						<VerticalSpacer />

						{/* Repeat password input */}
						{!formState.repeatPasswordHidden &&
							<div style={{ display: "flex", flexDirection: "column" }}>

								<label>Repeat Password</label>
								<input type="password"
									placeholder="Password"
									onChange={repeatPasswordWatcher} />
								{pwdNotMatching && <NotMatchingPasswordError />}

							</div>
						}

						<VerticalSpacer />

						{/* Button container */}
						<div style={{ display: "flex", justifyContent: "center" }}>
							<button style={{
								width: "30%"
							}}
								onClick={mainButtonClick}
							>{formState.mainButtonTxt}</button>
						</div>
					</div>
				</div>}
				{/* </Modal> */}

			</Overlay>

		</div >
	);
}