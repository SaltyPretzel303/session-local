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

	// Instead of holding references to elements, reference only values
	// with useState instead of useRef, that way validaion will be easier/shorter
	// since values will be either string or "" (or whatever is passed as a 
	const statusRef = useRef<HTMLLabelElement>(null)
	const emailRef = useRef<HTMLInputElement>(null)
	const usernameRef = useRef<HTMLInputElement>(null)
	const pwdRef = useRef<HTMLInputElement>(null)
	const repPwdRef = useRef<HTMLInputElement>(null)

	const registerPath = "http://localhost/auth/register"
	const authenticatePath = "http://localhost/auth/authenticate"
	// const authenticatePath = "http://localhost:8003/authenticate"

	async function loginClick() {
		setInRegState(false)

		console.log("Trying to login ... ")
		console.log(`Email: ${emailRef.current?.value}`)
		console.log(`Pwd: ${pwdRef.current?.value}`)
		console.log(`Path: ${authenticatePath}`)

		if (anyClear([emailRef.current, pwdRef.current])) {
			console.log("Please fill credentials ... ")
			return
		}

		const email: string = strOrEmpty(emailRef.current)
		const password: string = strOrEmpty(pwdRef.current)

		const loginRequest = formLoginRequest(email, password)

		let login_res = await fetch(authenticatePath,
			{
				method: "POST",
				headers: {
					'Content-type': 'application/json',
					// 'Access-Control-Allow-Credentials': 'true',
					// 'Access-Control-Allow-Origin': '*'
				},
				credentials: 'same-origin',
				body: JSON.stringify(loginRequest),
				// mode: 'cors'
			})

		if (login_res.status != 200) {
			console.log("Login failed miserably .. ")
			showMessage("Error ... try again ... ")
			return;
		}

		props.authSuccess({ username: "someone", email: "mail", following: [] })

	}

	function formLoginRequest(email: string, password: string) {
		return { email: email, password: password }
	}


	function showMessage(msg: string) {
		if (statusRef.current !== null) {
			statusRef.current.textContent = msg
		}
	}

	async function registerClick() {
		if (!inRegState) {
			setInRegState(true)
		} else {
			console.log("Trying to register ... ")
			console.log(`Email: ${emailRef.current?.value} `)
			console.log(`Pwd: ${pwdRef.current?.value} `)

			const inputFields = [
				emailRef.current,
				usernameRef.current,
				pwdRef.current,
				repPwdRef.current]

			if (anyClear(inputFields)) {
				console.log("Please fill all inputs ... ")
				return;
			}

			if (validEmail(emailRef.current?.value) &&
				validUsername(usernameRef.current?.value) &&
				validPassword(pwdRef.current?.value) &&
				matchingPwd(pwdRef.current?.value, repPwdRef.current?.value)) {

				const email: string = strOrEmpty(emailRef.current)
				const username = strOrEmpty(usernameRef.current)
				const pwd = strOrEmpty(pwdRef.current)
				// const rPwd = strOrEmpty(repPwdRef.current)

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

				console.log("HEADERS: ")
				console.log(reg_res.headers)
				console.log()
				console.log("DATA: ")
				console.log(data)

				setInRegState(false)

			} else {
				console.log("Please provide valid credentials ... ")
				return;
			}


		}
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

				<label ref={statusRef} hidden={true} />

				<label>Email address:</label>
				<input type="text" placeholder="Enter email .. " ref={emailRef} />

				<label hidden={!inRegState}>Username:</label>
				<input hidden={!inRegState} type="text" placeholder="Enter username ... " ref={usernameRef} />

				<label>Password</label>
				<input type="password" placeholder="Enter password ... " ref={pwdRef} />

				<label hidden={!inRegState}>Password again</label>
				<input hidden={!inRegState} type="password" placeholder="Repeat password ... " ref={repPwdRef} />

				<button onClick={loginClick}>Login</button>
				<button onClick={registerClick}>Register</button>

				<button onClick={closeClick}>close</button>
			</div>
		</div>
	)
}