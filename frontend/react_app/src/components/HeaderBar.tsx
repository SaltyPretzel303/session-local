import { useEffect, useState } from "react";
import LoginPopup from "./LoginPopup";
import { UserInfo } from '../Datas'
import UserInfoPopup from "./UserInfoPopup";

type HeaderBarProps = {
	loginVisible: boolean
	setLoginVisible: React.Dispatch<boolean>
	forcedLogin: boolean
	loggedIn: boolean
	getUser: () => Promise<UserInfo | undefined>
	logoutHandler: () => void
}

const standardSpacerSize = 10

function Spacer({ size }: { size: number }) {
	return (
		<div style={{ width: `${size}vh` }}></div>
	)
}

export default function HeaderBar(props: HeaderBarProps) {

	// const [loginVisible, setLoginVisible] = useState(false)
	const [userInfoVisible, setUserInfoVisible] = useState(false)
	const [profileLabel, setProfileLabel] = useState<string>('Profile')

	useEffect(() => {
		console.log("Rendering header bar.")
		if (props.loggedIn) {
			console.log("User is logged in.")
			loadProfileLabel()
		}

		console.log("User not logged in.")

	}, [props.loggedIn])

	async function loadProfileLabel() {
		let user = await props.getUser()
		if (user == undefined) {
			return
		}

		setProfileLabel(user.username)
	}

	return (
		<div className="flex flex-row 
				size-full
				justify-center items-center
				p-2
				bg-sky-800">

			<input placeholder="Search"
				className='basis-1/4 rounded-full placeholder p-2' />

			{<Spacer size={standardSpacerSize} />}

			{!props.loggedIn && <button
				className='basis-1/8 bg-purple-600 p-2 rounded-full'
				onClick={() => props.setLoginVisible(true)}>
				Sign In
			</button>}

			<LoginPopup
				loginVisible={props.loginVisible}
				setLoginVisible={props.setLoginVisible}
				forcedLogin={props.forcedLogin}
			/>

			{props.loggedIn && <button
				className='basis-1/8 bg-orange-500 p-2 rounded-full'
				onClick={() => setUserInfoVisible(true)}>
				{profileLabel}
			</button>}

			<UserInfoPopup isVisible={userInfoVisible}
				getUser={props.getUser}
				setVisible={setUserInfoVisible}
				logoutHandler={props.logoutHandler}
			/>


		</div>
	)
}