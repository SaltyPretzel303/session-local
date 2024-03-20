import { useEffect, useState } from "react";
import LoginPopup from "./LoginPopup";
import Session, { SessionContextType, signOut } from "supertokens-auth-react/recipe/session";
import StreamKeyPopup from "./StreamKeyPopup";
import { UserInfo } from '../Datas'
import UserInfoPopup from "./UserInfoPopup";

type HeaderBarProps = {
	userProvider: () => Promise<UserInfo | undefined>
}

const standardSpacerSize = 10
const smallSpaceSize = 1

function Spacer({ size }: { size: number }) {
	return (
		<div style={{ width: `${size}vh` }}></div>
	)
}

export default function HeaderBar(props: HeaderBarProps) {

	const headerStyle = {
		height: "5vh",
		padding: "10px",
		display: "flex",
		flexDirection: "row" as "row",
		justifyContent: "center",
		border: "2px solid black"
	};

	let context = Session.useSessionContext()

	const [loginVisible, setLoginVisible] = useState(false)
	const [streamKeyVisible, setStreamKeyVisible] = useState(false)
	const [userInfoVisible, setUserInfoVisible] = useState(false)

	useEffect(() => {
		if (context.loading) {
			return
		}
	}, [context])

	async function logoutClick() {
		if (!context.loading && context.doesSessionExist) {
			console.log("Will perform user signout.")
			await signOut()
			console.log("User signed out.")
		} else {
			if (context.loading) {
				console.log("Session is still loading")
			} else {
				console.log("Session is not loading")
				if (context.doesSessionExist) {
					console.log("Session exists")
				} else {
					console.log("Session does not exist")
				}
			}
			console.log("No session to sign out.")
		}
	}

	function streamClick() {
		setStreamKeyVisible(!streamKeyVisible)
	}

	function userInfoClick(){
		setUserInfoVisible(!userInfoVisible)
	}

	return (
		<div style={headerStyle}>

			<input placeholder="Search" style={{ width: "40vw" }}></input>

			{<Spacer size={standardSpacerSize} />}

			<button
				style={{ width: "10vw" }}
				onClick={() => setLoginVisible(true)}
				hidden={context.loading || context.doesSessionExist} >
				Sign In
			</button>

			<button
				style={{ width: "10vw" }}
				onClick={logoutClick}
				hidden={context.loading || !context.doesSessionExist}>
				LogOut
			</button>
			<LoginPopup loginVisible={loginVisible} setLoginVisible={setLoginVisible} />

			{<Spacer size={standardSpacerSize} />}

			{/* {<Spacer size={smallSpaceSize} />} */}

			{/* Grey out this button if not loggedIn  */}
			<button onClick={streamClick}>Stream</button>
			<StreamKeyPopup
				isVisible={streamKeyVisible}
				setIsVisible={setStreamKeyVisible} />

			<button onClick={userInfoClick}>User</button>
			<UserInfoPopup isVisible={userInfoVisible}
				provider={props.userProvider}
				setVisible={setUserInfoVisible} />

		</div>
	)
}