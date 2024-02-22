import { useEffect, useState } from "react";
import HlsPlayer from "./components/HlsPlayer";
import { useParams } from "react-router-dom";
import User from "./dataModel/User";
import { StreamInfo } from "./dataModel/StreamInfo";

const REGION: string = "eu"

type PlayerPageProps = {
	user: User | null
}

enum VideoQuality {
	HD = 'hd',
	SD = 'sd',
	SUBSD = 'subsd'
}

const MANIFEST_PATH = "index.m3u8"

export function PlayerPage(props: PlayerPageProps) {

	const { streamerName } = useParams<string>();
	const [streamSrc, setStreamSrc] = useState<string | undefined>(undefined)
	const [quality, setQuality] = useState<VideoQuality>(VideoQuality.SUBSD)

	useEffect(() => {

		console.log(`Launching player for: ${streamerName}`)

		if (props.user == null) {
			console.log("App has no valid user, please authenticate.")
			return;
		}

		if (!streamerName) {
			console.log("No channel provided.")
			return;
		}

		// Just because streamerName is string | undefined and not just string ...
		let creator: string = streamerName

		async function fetchStreamData() {
			try {
				let resp = await fetch(formGetInfoUrl(creator, REGION))

				if (!resp) {
					throw "Stream info fetch result empty ... "
				}

				if (resp.status !== 200) {
					throw resp.text
				}

				let txtData = await resp.text()
				console.log("Stream info fetched: " + txtData)

				let info = JSON.parse(txtData) as StreamInfo

				// let info = await resp.json() as StreamInfo

				// console.log("Received stream info ...")
				// console.log(info)

				// setStreamSrc(`${info.media_server.full_path}/${creator}_subsd/index.m3u8`)
				// setStreamSrc(`${info.media_server.full_path}`)
				setStreamSrc(formStreamUrl(info.media_server.full_path,
					creator,
					quality,
					MANIFEST_PATH))

			} catch (e) {
				console.log("Failed to fetch stream info: " + e)
				return
			}

		}

		fetchStreamData()

		// TODO display some loader or something ... 
	});

	function formGetInfoUrl(streamer: string, region: string) {
		return `http://localhost:8002/stream_info/${streamer}?region=${region}`
	}

	function formStreamUrl(path: string, streamer: string, quality: string, manifest: string) {
		return `${path}/${streamer}_${quality}/${manifest}`
	}

	// TODO move to config
	function formPosterUrl(streamer: string): string {
		return 'http://stream-registry.session:8002/tnial/' + streamer
	}

	return (
		<div className="streamPlayer">
			<HlsPlayer src={streamSrc}
				// streamerName has to defined 
				posterUrl={formPosterUrl(streamerName || "")}
				shouldPlay={false}
				quality={""}
				abr={false} 
				muted={false}/>
			{/* <Chat visible={true} /> */}

			<button onClick={() => setQuality(VideoQuality.HD)}>HD</button>
			<button onClick={() => setQuality(VideoQuality.SD)}>SD</button>
			<button onClick={() => setQuality(VideoQuality.SUBSD)}>SUBSD</button>

		</div>)
}