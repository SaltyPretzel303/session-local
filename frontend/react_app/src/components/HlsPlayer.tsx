import Hls, { HlsConfig } from "hls.js"
import { useEffect, useRef } from "react"
import "../style/Player.css"

export interface HlsPlayerProps {
	src: string | undefined
}

// export function HlsPlayer(props: HlsPlayerProps) {
export function HlsPlayer({ src }: { src: string | null }) {

	const videoRef = useRef<HTMLVideoElement>(null);

	useEffect(() => {

		console.log("Hls player setup for: " + src)

		const video = videoRef.current;
		if (!video) {
			return;
		}

		if (!src) {
			return
		}

		if (video.canPlayType("application/vnd.apple.mpegurl")) {
			console.log("This browser can play hls stream by default ... ")
			video.src = src

		} else if (Hls.isSupported()) {
			console.log("Using hls to play hls stream ... ")

			let config = {
				debug: true,
				xhrSetup: (header, url) => {
					header.withCredentials = true
					// header.setRequestHeader("Access-Control-Allow-Headers", "Content-Type, Accept, X-Requested-With")
					// header.setRequestHeader("Access-Control-Allow-Origin", "http://localhost:10000/");
					// header.setRequestHeader("Access-Control-Allow-Credentials", "true");

					// header.setRequestHeader("Cookie", "session=a512c8eb-1564-4a8d-83bb-f4c769eda3b0")
				}
			} as HlsConfig;

			const hls = new Hls(config)
			hls.loadSource(src)
			hls.attachMedia(video)
			// video.play()

		} else {
			console.log("We are unable to play stream in this browser ... ")
		}

	});

	return (<video
		style={{ border: "solid red 2px" }}
		className='streamVideo'
		ref={videoRef}
		autoPlay />)
}
