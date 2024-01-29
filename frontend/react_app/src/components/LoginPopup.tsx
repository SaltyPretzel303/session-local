import { useRef, useState } from "react"
import "../style/LoginPopup.css"
import {
	validEmail,
	validUsername,
	validPassword,
	matchingPwd,
	anyClear
} from "../Validators"
import User from "../data_model/User"
import { AuthResponse, isSuccess } from "../data_model/AuthResponse"
import axios, { AxiosRequestConfig } from "axios"

export interface LoginProps {
	// setUser: React.Dispatch<React.SetStateAction<User>>
	authSuccess: (user: User) => void
	// authFailure: (reason: string) => void;
	closed: () => void;
}

export function LoginPopup(props: LoginProps) {

	const [inRegState, setInRegState] = useState(false)

	const [status, setStatus] = useState("")
	const [email, setEmail] = useState("dd")
	const [username, setUsernamer] = useState("user_0")
	const [pwd, setPwd] = useState("pwd_0")
	const [rPwd, setRPwd] = useState("pwd_0")

	// const registerPath = "http://localhost/auth/register"
	const registerPath = "http://localhost:8003/register"
	// const authenticatePath = "http://localhost/auth/authenticate"
	const authenticatePath = "http://localhost:8003/authenticate"

	async function loginClick() {
		setInRegState(false)

		console.log("Trying to login ... ")
		console.log(`Email: ${username}`)
		console.log(`Pwd: ${pwd}`)
		console.log(`Path: ${authenticatePath}`)

		if (anyClear([username, pwd])) {
			console.log("Please fill credentials ... ")
			return
		}

		const loginRequest = formLoginRequest(username, pwd)

		try {

			let login_res = await fetch(authenticatePath,
				{
					method: "POST",
					headers: { 'Content-type': 'application/json', },
					// credentials: 'same-origin',
					body: JSON.stringify(loginRequest),
				})

			let rData = await login_res.json() as AuthResponse

			if (!rData) {
				throw new Error("Failed to parse received data.")
			}

			if (login_res.ok && isSuccess(rData)) {
				props.authSuccess(rData.user)
			} else {
				console.log("Authentication failed: " + rData.message)
				setStatus(rData.message)
			}

		} catch (err) {
			console.log("Authenticate request failed: " + err)
			setStatus("Error.")
		}
	}

	function formLoginRequest(username: string, password: string) {
		return { username: username, password: password }
	}


	function showMessage(msg: string) {
		setStatus(msg)
	}

	async function registerClick() {
		if (!inRegState) {
			setInRegState(true)
			return;
		}

		console.log("Trying to register ... ")
		console.log(`Email: ${email} `)
		console.log(`Pwd: ${pwd} `)

		if (anyClear([email, username, pwd, rPwd])) {
			console.log("Not all credentials provided.")
			setStatus("Fill all credentials.")

			return;
		}

		if (!validEmail(email) ||
			!validUsername(username) ||
			!validPassword(pwd) ||
			!matchingPwd(pwd, rPwd)) {

			console.log("Invalid credentials.")
			setStatus("Invalid credentials.")

			return;
		}

		const regRequest = formRegRequest(email, username, pwd)

		let reg_res = await fetch(registerPath,
			{
				method: "POST",
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(regRequest),
				credentials: "include"
				// mode: "cors"

			});

		if (!reg_res.ok) {
			console.log("Registration failed miserably ...")
			return
		}

		console.log("Registration successfull ... ")
		let data = await reg_res.json()

		setInRegState(false)



	}

	function formRegRequest(email: string, username: string, password: string) {
		return { email: email, username: username, password: password }
	}

	function strOrEmpty(inEl: HTMLInputElement | null) {
		return (inEl === null || inEl.value === undefined) ? "" : inEl.value
	}

	function closeClick() {
		props.closed()
	}

	return (
		<div className="LoginPopup">
			<div className="LoginInputsContainer">

				<label hidden={status === ""} >{status}</label>

				<label>Username:</label>
				<input type="text"
					placeholder="Enter username ... "
					value={username}
					onChange={(inEl) => setUsernamer(inEl.target.value)} />

				<label hidden={!inRegState}>Email address:</label>
				<input hidden={!inRegState} type="text" placeholder="Enter email .. "
					value={email}
					onChange={(inEl) => setEmail(inEl.target.value)} />

				<label>Password</label>
				<input type="password"
					placeholder="Enter password ... "
					value={pwd}
					onChange={(inEl) => setPwd(inEl.target.value)} />

				<label hidden={!inRegState}>Password again</label>
				<input hidden={!inRegState}
					type="password"
					placeholder="Repeat password ... "
					value={rPwd}
					onChange={(inEl) => setRPwd(inEl.target.value)} />

				<button onClick={loginClick}>Login</button>
				<button onClick={registerClick}>Register</button>

				<button onClick={closeClick}>close</button>
			</div>
		</div>
	)
}