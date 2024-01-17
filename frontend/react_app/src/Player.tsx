import { useEffect, useState } from "react";
import Chat from "./components/Chat";
import { HlsPlayer } from "./components/HlsPlayer";
import { useParams } from "react-router-dom";
import User from "./data_model/User";
import { StreamInfo } from "./data_model/StreamInfo";

export interface PlayerProps {
	user: User | null
}

export function Player(props: PlayerProps) {

	const { streamer } = useParams();
	const [streamSrc, setStreamSrc] = useState<string>("")

	useEffect(() => {
		console.log(`Launching player for: ${streamer}`)

		let creator = streamer !== undefined ? streamer : ""

		if (creator === "") {
			return;
		}

		async function fetchStreamData() {
			let resp: Response | undefined
			try {
				resp = await fetch(formGetInfoUrl(creator, "eu"))

				if (!resp) {
					throw "Stream info fetch result empty ... "
				}
				if (resp.status !== 200) {
					throw resp.text
				}
			} catch (e) {
				console.log("Failed to fetch stream info: " + e)
				return
			}

			let txt_data = await resp.text()
			console.log("Stream info fetched: " + txt_data)

			let info = JSON.parse(txt_data) as StreamInfo

			// let info = await resp.json() as StreamInfo

			// console.log("Received stream info ...")
			// console.log(info)

			setStreamSrc(`${info.media_server.full_path}/${creator}_subsd/index.m3u8`)
			// index.m3u8 should also be in info 

		}

		fetchStreamData()

		// TODO display some loader or something ... 

	}, []);

	function formGetInfoUrl(streamer: string, region: string) {
		return `http://localhost/reg/stream_info/${streamer}?region=${region}`
	}


	return (
		<div className="streamPlayer">
			{/* <HlsPlayer src={"http://localhost:10000/live/streamer_subsd/index.m3u8"} /> */}
			<HlsPlayer src={streamSrc} />
			{/* <Chat visible={true} /> */}
		</div>)
}