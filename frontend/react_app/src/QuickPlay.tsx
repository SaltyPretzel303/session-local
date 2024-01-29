import { useEffect, useRef, useState } from "react";
import { HlsPlayer } from "./components/HlsPlayer";
import Hls, { HlsConfig } from "hls.js";
import doRequest from './CookieSender'

export default function QuickPlay() {

	const videoRef = useRef<HTMLVideoElement>(null)
	const [updateFlag, setUpdateFlag] = useState<boolean>(true)
	const [source, setSource] = useState<string | undefined>(undefined)
	const [hls, setHls] = useState<Hls | null>(null)

	useEffect(() => {
		// Setup stream source

		console.log("Attaching hls to the player.")

		const video = videoRef.current

		if (!video || !hls || !source) {
			return
		}

		hls.loadSource(source)
		hls.attachMedia(video)

	}, [hls, source, updateFlag])

	function onClickHandler() {
		fetch('http://localhost:8003/authenticate',
			{
				method: "POST",
				credentials: "include",
				body: JSON.stringify(getAuthData()),
				headers: { 'Content-type': 'application/json' },
			})
			.then(res => {
				console.log("Authentication successfull.")

				let config = {
					// debug: true,
					xhrSetup: (xhr: XMLHttpRequest, url) => {
						xhr.withCredentials = true;
					},
					// Explore this options 
					// https://github.com/video-dev/hls.js/blob/master/docs/API.md#maxmaxbufferlength
					// backBufferLength: 0,
					// liveDurationInfinity: true,
				} as HlsConfig;

				setHls(new Hls(config))
				setSource("http://localhost:10000/live/user_0_subsd/index.m3u8")

			})
			.catch(err => {
				console.log("Error in authentication.")
				console.log(err)
			})
	}

	function getAuthData() {
		return { 'username': 'user_1', 'password': 'pwd_1' }
	}

	function pauseHandler() {
		console.log("Using pause handler.")
		if (!hls) {
			return
		}

		hls.stopLoad()
	}

	function playHandler() {
		console.log("Using play handler.")
		if (!hls) {
			return
		}

		// This will cause infinite loop of calling useEffect on hls
		// setUpdateFlag(!updateFlag)
	}

	return (<div>

		<div>
			<button onClick={onClickHandler}>Login button</button>
			<video className='streamVideo'
				style={{ border: "solid red 2px" }}
				ref={videoRef}
				autoPlay
				controls={true}
				onPause={pauseHandler}
			// onPlay={playHandler}
			/>
		</div>


	</div>)
}
