import Overlay from 'react-modal'
import { useEffect, useState } from 'react'
import {
	UserInfo,
	KeyResponse,
	isKeySuccess,
	failure as keyFailure
} from '../Datas'

import config from '../Config'

type userInfoProps = {
	isVisible: boolean
	setVisible: React.Dispatch<boolean>
	logoutHandler: () => void
	getUser: () => Promise<UserInfo | undefined>
}

export default function UserInfoPopup(props: userInfoProps) {

	const [userInfo, setUserInfo] = useState<UserInfo | undefined>(undefined)
	const [streamKeyError, setStreamKeyError] = useState<string | undefined>(undefined)
	const [isLoadingKey, setIsLoadingKey] = useState<boolean>(false)
	const [streamKey, setStreamKey] = useState<KeyResponse | undefined>(undefined)

	useEffect(() => {
		if (!props.isVisible) {
			return
		}

		if (props.isVisible && streamKey && isExpired(streamKey.exp_date)) {
			console.log("Key expired, clearing previous data.")
			setStreamKey(undefined)
			setStreamKeyError("Key expired, request new.")
		}

		console.log("Will fetch user data.")
		props.getUser()
			.then((userData) => {
				console.log("Data fetched: " + userData)
				setUserInfo(userData)
			})
			.catch((err) => {
				console.log("Failed to fetch data: " + err)
			})

	}, [props.isVisible])

	function isExpired(expDate: string) {
		return (new Date(expDate)) < new Date()
	}

	async function revealStreamKeyClick() {
		setIsLoadingKey(true)
		let keyResponse = await fetchKey(config.streamKeyUrl)

		if (!isKeySuccess(keyResponse.status)) {
			setStreamKeyError(keyResponse.message)

			setIsLoadingKey(false)
			setStreamKey(undefined)
			setStreamKeyError(keyResponse.message)

			return
		}

		setStreamKey(keyResponse)
		setIsLoadingKey(false)
		setStreamKeyError(undefined)
	}

	async function fetchKey(keyUrl: string): Promise<KeyResponse> {
		console.log("Will request stream key.")
		return fetch(keyUrl)
			.then(async (res) => {
				if (res.status != 200) {
					console.log("Got non 200 code for stream key.")
					keyFailure("Failed to obtain stream key")
				}

				// console.log("Response: ")
				// console.log(await res.text())

				return (await res.json()) as KeyResponse
			})
			.catch((err) => {
				console.log("Error while fetching stream key: " + err)
				return keyFailure("Failed to obtain stream key.")
			})
	}

	function logoutClick() {
		props.setVisible(false)
		props.logoutHandler()
	}


	function StreamKey() {
		if (isLoadingKey) {
			return (
				<img
					style={{
						margin: "0px",
						padding: "0px",
						width: "10%",
						height: "30	%"
					}}
					src={"loading.gif"} />
			)
		} else {
			if (streamKey) {
				return (
					<p>{streamKey.value}</p>
				)
			} else {
				return (
					<button
						style={{
							fontSize: "20px",
							background: "#f2f1ed",
							border: "none"
						}
						}
						onClick={revealStreamKeyClick}
					> Click to reveal the key</button >
				)
			}
		}
	}

	function formatDate(strDate: string): string {
		return (new Date(strDate)).toLocaleString("de-CH")
	}

	return (
		<Overlay
			style={{
				content: {
					display: "flex",
					alignItems: "center",
					justifyContent: "center"
				}
			}}
			ariaHideApp={false}
			isOpen={props.isVisible}
			shouldCloseOnEsc={true}
			onRequestClose={() => props.setVisible(false)}>

			<div
				style={{
					padding: "30px",
					borderRadius: "20px",
					width: "30vw",
					display: "flex",
					flexDirection: "column",
					alignItems: "center",
					textAlign: "center",
					border: "2px solid orange"
				}}
			>

				<h2>Username: {userInfo?.username}</h2>
				<h2>Email: {userInfo?.email}</h2>

				<hr style={{ width: "100%" }}></hr>

				<h1>Start Streaming</h1>
				<p>
					In order to stream take this secret key and paste it in
					you streaming client (obs or similar software).
				</p>

				{/* Error message  */}
				{streamKeyError && <p style={{ color: "red" }}>{streamKeyError}</p>}

				{/* Stream key container */}
				<div
					style={{
						background: "#f2f1ed",
						padding: "0px",
						margin: "0px",
						borderBottom: "2px solid brown",
						width: "70%",
						height: "5vh",
						display: "flex",
						flexDirection: "row",
						justifyContent: "center",
						alignItems: "center",
						textAlign: "center",
						fontSize: "20px"
					}}
				>

					<StreamKey />

				</div>

				{/* Expiration date and DoNotShare message */}
				{streamKey &&
					<div style={{
						display: "flex",
						flexDirection: "column"
					}}>

						<p>Key will expire at: {formatDate(streamKey?.exp_date)}</p>
						<p style={{ fontWeight: "bold" }}>Do not share this key !!!</p>
					</div>
				}

				<hr style={{ width: "100%" }}></hr>

				<button onClick={logoutClick}>Logout</button>
			</div>

		</Overlay>
	)
}
