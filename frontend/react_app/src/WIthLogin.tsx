import { LoginPopup } from "./components/LoginPopup";
import User from "./data_model/User";


export interface WithLoginProps {
	children: React.ReactNode[] | React.ReactNode
	setUser: React.Dispatch<React.SetStateAction<User | null>>
	setLoginDenied: React.Dispatch<React.SetStateAction<boolean>>
	showLogin: boolean
}

export function WithLogin(props: WithLoginProps) {

	function loginHandler(user: User) {
		console.log("Handling AuthSuccessfull action ... ")
		if (user != null) {
			console.log("Setting user ... ")
			props.setUser(user)
		}
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