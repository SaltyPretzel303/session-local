import Hls, { BufferEOSData, Events, HlsConfig } from "hls.js"
import { useEffect, useRef, useState } from "react"
import config from '../Config'


type HlsPlayerProps = {
	src: string | undefined,
	posterUrl: string | undefined,
	shouldPlay: boolean,
	quality: string,
	abr: boolean // if false, passed quality is forced
	muted: boolean
	onDone?: () => void
}

export default function HlsPlayer(props: HlsPlayerProps) {

	const videoRef = useRef<HTMLVideoElement>(null);
	let hls: Hls | undefined = undefined

	useEffect(() => {
		console.log("Constructing hlsPlayer for: " + props.src)

		const videoElement = videoRef.current;
		if (!videoElement || !props.src) {
			console.log("Missing src or no video element.")
			return
		}

		if (videoElement.canPlayType("application/vnd.apple.mpegurl")) {
			console.log("This browser supports hls stream by default.")
			videoElement.src = props.src
		} else if (Hls.isSupported()) {
			let config = {
				// debug: true,
				xhrSetup: (xhr: XMLHttpRequest, url) => {
					xhr.withCredentials = true;
				},
				backBufferLength: 0,
				liveDurationInfinity: true
			} as HlsConfig;

			hls = new Hls(config)
			hls.loadSource(props.src)
			hls.attachMedia(videoElement)

			if (props.shouldPlay) {
				console.log("Stream will be played.")

				hls.on(Hls.Events.BUFFER_EOS, doneHandler)
				hls.startLoad()
				// videoElement.play()
				// videoElement.play()
				// 	.then((res) => {
				// 		console.log("Video  successfully started.")
				// 	})
				// 	.catch((err) => {
				// 		console.log("Failed to start video: " + err)
				// 	})
			} else {
				console.log("Stream will not be played.")
				hls.stopLoad()
			}

		} else {
			console.log("Unable to play stream in this browser ... ")
		}

		return () => {
			console.log("Destroying hlsPlayer.")
			if (hls) {
				hls.detachMedia()
				hls.destroy()
			}
		}

	}, [props]);

	function doneHandler(event: Events.BUFFER_EOS, data: BufferEOSData) {
		console.log("Handling stream done in hlsPlayer.")
		props.onDone?.()
	}

	// not sure if this one is implemented correctly
	function pauseHandler() {
		if (!hls) {
			console.log("Pause ignored, hls is undefined.")
			return
		}

		hls.stopLoad()
		console.log("Pause handled, load stopped.")
	}



	return (
		<div className="box-border" >
			<video
				className='border border-black w-full h-full'
				muted={props.muted}
				poster={props.posterUrl}
				ref={videoRef}
				onPause={pauseHandler}
				autoPlay
			/>
		</div>
	)
}
