import { useEffect, useState } from "react";
import LoginPopup from "./LoginPopup";
import { StreamInfo, UserInfo } from '../Datas'
import UserInfoPopup from "./UserInfoPopup";
import Search from "./Search";

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

	// useEffect(() => {

	// 	if (user == undefined) {
	// 		getUser()
	// 	}

	// 	if (stream == undefined) {
	// 		getStream()
	// 	}

	// }, [user, stream])

	function LogoText() {

		let offline = 'text-orange-600'
		let online = 'text-red-600'
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
				bg-slate-900
				border-b-2 border-b-slate-800
				">

			{/* left section  */}
			<div className='flex flex-row w-1/3 h-full justify-left items-center'>

				<img className='flex h-full mr-4' src="broadcast.png" />
				<LogoText />

			</div>

			{/* middle section  */}
			<div className='flex flex-row
				min-w-[600px]
				w-1/3 h-full
				justify-center items-center'>

				<div className='flex flex-col
					w-1/2 h-full
					relative justify-center items-center
					z-50'>

					{/* <Search getUser={getUser} /> */}

				</div>
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