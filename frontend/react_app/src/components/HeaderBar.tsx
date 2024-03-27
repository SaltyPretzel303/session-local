import { useEffect, useState } from "react";
import LoginPopup from "./LoginPopup";
import { UserInfo } from '../Datas'
import UserInfoPopup from "./UserInfoPopup";

type HeaderBarProps = {
	loggedIn: boolean
	userProvider: () => Promise<UserInfo | undefined>
	logoutHandler: () => void
}

const standardSpacerSize = 10

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

	const [loginVisible, setLoginVisible] = useState(false)
	const [userInfoVisible, setUserInfoVisible] = useState(false)

	return (
		<div style={headerStyle}>

			<input placeholder="Search" style={{ width: "40vw" }}></input>

			{<Spacer size={standardSpacerSize} />}

			{!props.loggedIn && <button
				style={{ width: "10vw" }}
				onClick={() => setLoginVisible(true)}>
				Sign In
			</button>}

			<LoginPopup
				loginVisible={loginVisible}
				setLoginVisible={setLoginVisible}
			/>

			{props.loggedIn && <button
				onClick={() => setUserInfoVisible(true)}>
				User
			</button>}

			<UserInfoPopup isVisible={userInfoVisible}
				getUser={props.userProvider}
				setVisible={setUserInfoVisible}
				logoutHandler={props.logoutHandler}
			/>


		</div>
	)
}