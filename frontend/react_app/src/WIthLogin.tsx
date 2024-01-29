import { useState } from "react";
import { Player } from "./Player";
import { LoginPopup } from "./components/LoginPopup";
import User from "./data_model/User";


export interface WithLoginProps {
	children: React.ReactNode[] | React.ReactNode
	setUser: React.Dispatch<React.SetStateAction<User | null>>
	setLoginDenied: React.Dispatch<React.SetStateAction<boolean>>
	showLogin: boolean
}

export function WithLogin(props: WithLoginProps) {

	const [pUser, setPUser] = useState<User | null>(null)

	function loginHandler(user: User) {
		console.log("Handling AuthSuccessfull action ... ")

		console.log("Will set user|null")

		props.setUser(user)
		setPUser(user)
	}

	function closeHandler() {
		console.log("Handling LoginFormClosed action ... ")
		props.setLoginDenied(true)
	}

	return (
		<div>
			{props.showLogin ? <LoginPopup authSuccess={loginHandler} closed={closeHandler} /> : null}
			{props.children}
		</div>
	);
}