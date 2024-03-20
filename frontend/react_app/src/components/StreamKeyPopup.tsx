import { Dispatch, useEffect, useState } from 'react'
import Overlay from 'react-modal'
import config from "../Config"
import { KeyResponse, isKeySuccess, failure as keyFailure } from '../Datas'

type StreamKeyPopupProps = {
	isVisible: boolean
	setIsVisible: Dispatch<boolean>
}

export default function StreamKeyPopup(props: StreamKeyPopupProps) {

	const [streamKey, setStreamKey] = useState<KeyResponse | undefined>(undefined)
	const [isLoadingKey, setIsLoadingKey] = useState(false)
	const [error, setError] = useState<string | undefined>(undefined)

	useEffect(() => {
		console.log("Rendering key popup.")
		if (props.isVisible && streamKey && isExpired(streamKey.exp_date)) {
			console.log("Key expired, clearing previous data.")
			setStreamKey(undefined)
			setError("Key expired, request new.")
		}

	}, [props.isVisible])

	function isExpired(expDate: string) {
		return (new Date(expDate)) < new Date()
	}

	async function revealClick() {
		setIsLoadingKey(true)
		let keyResponse = await fetchKey(config.streamKeyUrl)

		if (!isKeySuccess(keyResponse.status)) {
			setError(keyResponse.message)

			setIsLoadingKey(false)
			setStreamKey(undefined)
			setError(keyResponse.message)

			return
		}

		setStreamKey(keyResponse)
		setIsLoadingKey(false)
		setError(undefined)
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

	function formatDate(strDate: string): string {
		return (new Date(strDate)).toLocaleString("de-CH")
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

				{/* Error message  */}
				{error && <p style={{ color: "red" }}>{error}</p>}

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
			</div>

		</Overlay >

	)
}