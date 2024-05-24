import { useEffect, useState } from "react";
import LoginPopup from "./LoginPopup";
import { StreamInfo, UserInfo } from '../Datas'
import UserInfoPopup from "./UserInfoPopup";

type HeaderBarProps = {
	loginVisible: boolean
	setLoginVisible: React.Dispatch<boolean>
	forcedLogin: boolean
	user: UserInfo | undefined
	getUser: () => Promise<UserInfo | undefined>
	stream: StreamInfo | undefined
	getStream: () => Promise<StreamInfo | undefined>
	logoutHandler: () => void
}

export default function HeaderBar({
	loginVisible,
	setLoginVisible,
	forcedLogin,
	user,
	getUser,
	stream,
	getStream,
	logoutHandler
}: {
	loginVisible: boolean
	setLoginVisible: React.Dispatch<boolean>
	forcedLogin: boolean
	user: UserInfo | undefined
	getUser: () => Promise<UserInfo | undefined>
	stream: StreamInfo | undefined
	getStream: () => Promise<StreamInfo | undefined>
	logoutHandler: () => void
}) {

	const [userInfoVisible, setUserInfoVisible] = useState(false)

	useEffect(() => {

		if (user == undefined) {
			getUser()
		}

		if (stream == undefined) {
			getStream()
		}

	}, [user, stream])

	function LogoText() {

		let offline = 'text-orange-600'
		let online = 'text-red-500'
		let textColor = stream ? online : offline

		return (
			// also customize font
			<div className={`flex h-full items-center
				text-bold ${textColor} text-[35px] 
				font-['Bebas Neue']`}>
				<p>SESSION</p>
			</div>
		)

	}

	function LoginButton() {

		return (
			<button
				className='flex h-full w-[160px]
					justify-center items-center
					px-2 rounded-full 
					bg-orange-500 border border-orange-400'
				onClick={() => user ? setUserInfoVisible(true) : setLoginVisible(true)}>
				{user ? user.username : "Sign in / Sign up"}
			</button>
		)

	}


	return (
		<div className="flex flex-row 
				size-full 
				px-10
				justify-center items-center
				font-[Oswald]
				bg-gradient-to-t from-slate-800 from-1%  to-slate-900
				">

			{/* left section  */}
			<div className='flex flex-row w-1/3 h-full justify-left items-center'>

				<img className='flex h-full mr-4' src="broadcast.png" />

				<LogoText />

			</div>

			{/* middle section  */}
			<div className='flex flex-row w-1/3 h-full
				justify-start items-center'>

				<input className='flex w-3/5 h-2/3
					rounded-full px-4'

					placeholder="Search" />

				{/* TODO dropdown list in form of some popup ...  */}
			</div>



			{/* right section  */}
			<div className='flex flex-row w-1/3 h-full 
				justify-end items-center
				py-2 pr-10'>

				<LoginButton />

			</div>

			{/* popups activated from the headerbar */}

			<LoginPopup
				loginVisible={loginVisible}
				setLoginVisible={setLoginVisible}
				forcedLogin={forcedLogin}
			/>

			<UserInfoPopup isVisible={userInfoVisible}
				user={user}
				getUser={getUser}
				stream={stream}
				getStream={getStream}
				setVisible={setUserInfoVisible}
				logoutHandler={logoutHandler}
			/>

		</div>
	)
}