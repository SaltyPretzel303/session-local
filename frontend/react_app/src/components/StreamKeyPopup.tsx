import { Dispatch, useState } from 'react'
import Overlay from 'react-modal'
import config from "../Config"
import { Stream } from 'stream'
import { KeyResponse, isSuccess } from '../dataModel/StreamKeyResponse'

type StreamKeyPopupProps = {
	isVisible: boolean
	setIsVisible: Dispatch<boolean>
}

export default function StreamKeyPopup(props: StreamKeyPopupProps) {

	const [streamKey, setStreamKey] = useState("soPJv92-s")
	const [expirationDate, setExpirationData] = useState("10.2.2029 14:13")
	const [keyRevealed, setKeyRevealed] = useState(false)
	const [loadingKey, setLoadingKey] = useState(false)

	function revealClick() {
		// fetch key
		setLoadingKey(true)

		setTimeout(() => {
			console.log("Resolved.")
			setLoadingKey(false)
			setKeyRevealed(true)
		}, 2000);

	}

	async function fetchKey() {
		console.log("Will request stream key.")
		fetch(config.streamKeyUrl)
			.then(async (res) => {
				if (res.status != 200) {
					console.log("Got non 200 code for stream key")
					return
				}

				let jsonStr = await res.json()
				let resp: KeyResponse = JSON.parse(jsonStr)

				if (!isSuccess(resp.status)) {
					console.log("Key response failed with: " + resp.message)
					return
				}

				setStreamKey(resp.value)
				setExpirationData(resp.exp_data)
			})
	}

	function StreamKey() {
		if (loadingKey) {
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
			if (keyRevealed) {
				return (
					<p>{streamKey}</p>
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
						onClick={revealClick}
					> Click to reveal the key</button >
				)
			}
		}
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
			onRequestClose={() => props.setIsVisible(false)}>

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

				<h1>Start Streaming</h1>
				<p>
					In order to stream take this secret key and paste it in
					you streaming client (obs or similar software).
				</p>


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

				<p>Key will expire at: {expirationDate}</p>
				<p style={{ fontWeight: "bold" }}>Do not share this key !!!</p>
			</div>

		</Overlay>

	)
}