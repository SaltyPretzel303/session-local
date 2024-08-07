import Hls, { BufferEOSData, Events, HlsConfig } from "hls.js"
import { useEffect, useRef, useState } from "react"


export default function HlsPlayer(
	{
		src,
		posterUrl,
		shouldPlay,
		muted,
		onDone
	}: {
		src: string | undefined,
		posterUrl: string | undefined,
		shouldPlay: boolean,
		muted: boolean,
		onDone?: () => void
	}) {

	const videoRef = useRef<HTMLVideoElement>(null);
	let hls: Hls | undefined = undefined
	// const [hls, setHls] = useState<Hls | undefined>(undefined)

	let timer: NodeJS.Timer | undefined = undefined
	const [bitrate, setBitrate] = useState("0")

	useEffect(() => {
		// console.log("Constructing hlsPlayer for: " + src)

		const videoElement = videoRef.current;
		if (!src || !videoElement) {
			console.log("Missing src or no video element.")
			return
		}

		if (videoElement.canPlayType("application/vnd.apple.mpegurl")) {
			console.log("This browser supports hls stream by default.")
			videoElement.src = src
		} else if (Hls.isSupported()) {
			let config = {
				// debug: true,
				xhrSetup: (xhr: XMLHttpRequest, url) => {
					xhr.withCredentials = true;
				},
				backBufferLength: 0,
				liveDurationInfinity: true,
				abrEwmaFastLive: 3
			} as HlsConfig;


			hls = new Hls(config)


			hls.loadSource(src)
			hls.attachMedia(videoElement)

			if (shouldPlay) {
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

			// setHls(mhls)

			timer = setInterval(() => {
				if (hls) {
					// setBitrate(Math.trunc(hls.bandwidthEstimate / 1000) +
					// "k")
					let value = Math.trunc(hls.bandwidthEstimate / 1000)
					// console.log(value)
					setBitrate(value + "k")
				}
			}, 1000)

		} else {
			console.log("Unable to play stream in this browser ... ")
		}

		return () => {
			// console.log("Destroying hlsPlayer.")
			if (hls) {
				hls.detachMedia()
				hls.destroy()
			}

			if (timer) {
				clearInterval(timer)
			}
		}

	}, [src, shouldPlay]);

	function doneHandler(event: Events.BUFFER_EOS, data: BufferEOSData) {
		console.log("Handling stream done in hlsPlayer.")
		onDone?.()
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

	function setLevel(lv: number) {
		console.log("Setting level: " + lv)
		if (hls) {
			console.log("Hls ok")
			hls.loadLevel = lv
			console.log(hls.loadLevel)
		}
	}

	return (
		<video
			className='flex h-full'
			muted={muted}
			poster={posterUrl}
			ref={videoRef}
			// onPause={pauseHandler}
			autoPlay
		/>
	)
}
