import Overlay from 'react-modal'
import { useEffect, useState } from 'react'
import { UserInfo } from '../Datas'


type userInfoProps = {
	isVisible: boolean
	setVisible: React.Dispatch<boolean>
	provider: () => Promise<UserInfo | undefined>
}

export default function UserInfoPopup(props: userInfoProps) {

	const [data, setData] = useState<UserInfo | undefined>(undefined)

	useEffect(() => {
		if (!props.isVisible) {
			return
		}

		console.log("Will fetch user data.")
		props.provider()
			.then((userData) => {
				console.log("Data fetched: " + userData)
				setData(userData)
			})
			.catch((err) => {
				console.log("Failed to fetch data: " + err)
			})

	}, [props.isVisible])

	return (
		<Overlay
			ariaHideApp={false}
			isOpen={props.isVisible}
			shouldCloseOnEsc={true}
			onRequestClose={() => props.setVisible(false)}>

			<h3>User data:</h3>
			{JSON.stringify(data)}

		</Overlay>
	)
}
