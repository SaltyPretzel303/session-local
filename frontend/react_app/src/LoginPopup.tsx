import { useRef, useState } from "react"
import "./LoginPopup.css"

export default function LoginPopup() {

	const [inRegState, setInRegState] = useState(false)
	const emailRef = useRef<HTMLInputElement>(null)
	const pwdRef = useRef<HTMLInputElement>(null)
	const repPwdRef = useRef<HTMLInputElement>(null)

	function registerClick() {
		if (!inRegState) {
			setInRegState(true)
		} else {
			console.log("you sir are registered ... ")
			console.log(`Email: ${emailRef.current?.value}`)
			console.log(`Pwd: ${pwdRef.current?.value}`)

			setInRegState(false)
		}
	}

	return (
		<div className="LoginPopupContainer">

			<label>Email address:</label>
			<input type="text" placeholder="Enter email .. " ref={emailRef} />

			<label>Password</label>
			<input type="password" placeholder="Enter password ... " ref={pwdRef} />

			<label hidden={!inRegState}>Password again</label>
			<input hidden={!inRegState} type="password" placeholder="Repeat password ... " ref={repPwdRef} />

			<button>Login</button>
			<button onClick={registerClick}>Register</button>

		</div>
	)
}

