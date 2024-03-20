import { useEffect, useState } from "react";
import HlsPlayer from "./components/HlsPlayer";
import { useParams } from "react-router-dom";
import { UserInfo } from "./Datas";
import { StreamInfo } from "./Datas";
import config from './Config'

// const REGION: string = "eu"

type PlayerPageProps = {
	getUser: () => Promise<UserInfo | undefined>
}

enum VideoQuality {
	HD = 'hd',
	SD = 'sd',
	SUBSD = 'subsd'
}

const MANIFEST_PATH = "index.m3u8"

export function PlayerPage(props: PlayerPageProps) {

	const [user, setUser] = useState<UserInfo | undefined>()

	const { streamer } = useParams<string>()
	const [streamSrc, setStreamSrc] = useState<string | undefined>(undefined)
	const [quality, setQuality] = useState<VideoQuality>(VideoQuality.SUBSD)

	useEffect(() => {
		console.log(`Launching player for: ${streamer}`)

		props.getUser().then((data) => setUser(data))

		if (!streamer) {
			console.log("No channel provided.")
			return;
		}

		// streamerName is string | undefined
		let creator: string = streamer

		async function fetchStreamData() {
			try {
				let resp = await fetch(config.streamInfoUrl(creator, config.region))

				if (!resp) {
					throw "Stream info fetch result empty ... "
				}

				if (resp.status !== 200) {
					throw resp.text
				}

				let txtData = await resp.text()
				console.log("Stream info fetched: " + txtData)

				let info: StreamInfo = JSON.parse(txtData)

				// let info = await resp.json() as StreamInfo

				// console.log("Received stream info ...")
				// console.log(info)

				// setStreamSrc(`${info.media_server.full_path}/${creator}_subsd/index.m3u8`)
				// setStreamSrc(`${info.media_server.full_path}`)
				// setStreamSrc(formStreamUrl(info.media_servers[0].access_url,
				// 	creator,
				// 	quality,
				// 	MANIFEST_PATH))
				// TODO filter available servers ... ? 
				// setStreamSrc(info.media_servers[0].access_url)
				setStreamSrc("http://cdn.session.com/live/streamer-0_subsd/index.m3u8")

			} catch (e) {
				console.log("Failed to fetch stream info: " + e)
				return
			}

		}

		fetchStreamData()

		// TODO display some loader or something ... 
	});

	function formGetInfoUrl(streamer: string, region: string) {
		return `http://session.com/stream/stream_info/${streamer}?region=${region}`
	}


	function formPosterUrl(streamer: string | undefined): string {
		return streamer ? config.tnailUrl(streamer) : config.notFoundTnailUrl()
	}

	return (
		<div className="streamPlayer">
			<HlsPlayer src={streamSrc}
				posterUrl={formPosterUrl(streamer)}
				shouldPlay={false}
				quality={""}
				abr={false}
				muted={false} />

			{/* <Chat visible={true} /> */}

			<button onClick={() => setQuality(VideoQuality.HD)}>HD</button>
			<button onClick={() => setQuality(VideoQuality.SD)}>SD</button>
			<button onClick={() => setQuality(VideoQuality.SUBSD)}>SUBSD</button>

		</div>)
}