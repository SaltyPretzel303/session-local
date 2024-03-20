import Hls, { CMCDController, EMEControllerConfig, HlsConfig } from "hls.js"
import React, { useEffect, useRef, useState } from "react"
import { MediaServer } from "../Datas"


type HlsPlayerProps = {
	src: string | undefined,
	posterUrl: string | undefined,
	shouldPlay: boolean,
	quality: string,
	abr: boolean // if false, passed quality is forced
	muted: boolean
}

export default function HlsPlayer(props: HlsPlayerProps) {

	const videoRef = useRef<HTMLVideoElement>(null);
	let hls: Hls | undefined = undefined

	useEffect(() => {
		console.log("Constructing hlsPlayer for: " + props.src)

		const videoElement = videoRef.current;
		if (!videoElement || !props.src) {
			console.log("HlsPlayer not initialized")
			console.log("Missing src or no video element.")
			return
		}

		if (videoElement.canPlayType("application/vnd.apple.mpegurl")) {
			console.log("This browser supports hls stream by default.")
			videoElement.src = props.src
		} else if (Hls.isSupported()) {
			console.log("Will use hls.js to play hls stream.")

			let config = {
				// debug: true,
				xhrSetup: (xhr: XMLHttpRequest, url) => {
					xhr.withCredentials = true;
				},
			} as HlsConfig;

			hls = new Hls(config)
			hls.loadSource(props.src)
			hls.attachMedia(videoElement)

			if (props.shouldPlay) {
				hls.startLoad()
				// videoElement.play()
				// 	.then((res) => {
				// 		console.log("Video  successfully started.")
				// 	})
				// 	.catch((err) => {
				// 		console.log("Failed to start video: " + err)
				// 	})
			} else {
				hls.stopLoad()
			}

		} else {
			console.log("Unable to play stream in this browser ... ")
		}

		return () => {
			console.log("Calling hlsPlayer destructor.")
			if (hls) {
				hls.detachMedia()
				hls.destroy()
			}
		}

	}, [props]);

	function pauseHandler() {
		if (!hls) {
			console.log("Pause ignored, hls is undefined.")
			return
		}

		hls.stopLoad()
		console.log("Pause handled, load stopped.")
	}


	return (
		<div style={
			{
				border: "1px solid purple",
				boxSizing: "border-box",
				width: "100%",
				height: "100%"
			}
		}
		>
			<video
				style={
					{
						border: "solid red 2px",
						width: "100%",
						height: "100%"
					}
				}
				muted={props.muted}
				poster={props.posterUrl}
				ref={videoRef}
				onPause={pauseHandler}
				// autoPlay
			/>
		</div>
	)
}
