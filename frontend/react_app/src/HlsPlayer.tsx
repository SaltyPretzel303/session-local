import Hls from "hls.js"
import { useEffect, useRef } from "react"

export default function HlsPlayer({ src }: { src: string }) {
	const videoRef = useRef<HTMLVideoElement>(null);


	useEffect(() => {

		const video = videoRef.current;
		if (!video) {
			return;
		}

		if (video.canPlayType("application/vnd.apple.mpegurl")) {
			console.log("This browser can play hls stream by default ... ")
			video.src = src

		} else if (Hls.isSupported()) {
			console.log("Using hls to play hls stream ... ")

			const hls = new Hls()
			hls.loadSource(src)
			hls.attachMedia(video)

		} else {
			console.log("We are unable to play stream in this browser ... ")
		}

	}, [src, videoRef]);

	return (<video ref={videoRef} />)
}