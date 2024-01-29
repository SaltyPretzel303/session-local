import Hls, { CMCDController, EMEControllerConfig, HlsConfig } from "hls.js"
import { useEffect, useRef, useState } from "react"
import "../style/Player.css"

export interface HlsPlayerProps {
	src: string | undefined
}

export function HlsPlayer(props: HlsPlayerProps) {

	const videoRef = useRef<HTMLVideoElement>(null);

	function getAuthData() {
		return { 'username': 'user_0', 'password': 'pwd_0' }
	}

	useEffect(() => {
		console.log("Preparing for: " + props.src)

		const video = videoRef.current;
		if (!video || !props.src) {
			return;
		}

		if (video.canPlayType("application/vnd.apple.mpegurl")) {
			console.log("This browser can play hls stream by default.")
			video.src = props.src
		} else if (Hls.isSupported()) {
			console.log("Using hls.js to play hls stream.")

			let config = {
				// debug: true,
				xhrSetup: (xhr: XMLHttpRequest, url) => {
					xhr.withCredentials = true;
				},
			} as HlsConfig;

			const hls = new Hls(config)
			hls.loadSource(props.src)
			hls.attachMedia(video)

		} else {
			console.log("We are unable to play stream in this browser ... ")
		}

	});

	return (
		<div>
			<video className='streamVideo'
				style={{ border: "solid red 2px" }}
				ref={videoRef}
				autoPlay />
		</div>
	)
}
