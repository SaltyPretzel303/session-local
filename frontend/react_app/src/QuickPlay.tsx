import { useEffect, useRef, useState } from "react";
import Hls, { HlsConfig } from "hls.js";

export default function QuickPlay() {

	const videoRef = useRef<HTMLVideoElement>(null)
	let hls: Hls | undefined = undefined

	useEffect(() => {
		console.log("Attaching hls to the player.")

		const video = videoRef.current

		// if (!video || !hls || !source) {
		// 	return
		// }
		if (!video) {
			return
		}

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

		hls = new Hls(config)
		hls.loadSource("http://localhost:10000/live/user0_subsd/index.m3u8")
		hls.attachMedia(video)

		console.log("Player set up.")
	})

	function pauseHandler() {
		console.log("Using pause handler.")
		if (!hls) {
			console.log("Hls object not found.")
			return
		}

		hls.stopLoad()
	}

	return (<div>

		<div>
			<video style={{ border: "solid red 2px" }}
				ref={videoRef}
				autoPlay
				controls={true}
				onPause={pauseHandler}
			/>
		</div>


	</div>)
}
