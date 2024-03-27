import { useEffect, useState } from "react";
import HlsPlayer from "./components/HlsPlayer";
import { useLocation, useParams } from "react-router-dom";
import { UserInfo } from "./Datas";
import { StreamInfo } from "./Datas";
import config from './Config'

type PlayerPageProps = {
	getUser: () => Promise<UserInfo | undefined>
	// streamData: StreamInfo | undefined
}

enum VideoQuality {
	HD = 'hd',
	SD = 'sd',
	SUBSD = 'subsd'
}

export function PlayerPage(props: PlayerPageProps) {

	const [user, setUser] = useState<UserInfo | undefined>()

	const { streamer } = useParams<string>()
	const [streamSrc, setStreamSrc] = useState<string | undefined>(undefined)
	const [quality, setQuality] = useState<VideoQuality>(VideoQuality.SUBSD)

	// Data provided using navigate programatically.
	// Mostly from stream preview.
	const { state } = useLocation()

	useEffect(() => {
		console.log(`Launching player for: ${streamer}`)

		if (!streamer) {
			console.log("No channel provided.")
			return;
		}

		if (state) {
			console.log("Stream data provided.")
			
			const { streamData }: { streamData: StreamInfo } = state
			setStreamSrc(streamData.media_servers[0].access_url)
		} else {
			console.log("Will fetch stream data.")

			// streamerName is string | undefined
			let creator: string = streamer
			fetchStreamData(creator)
		}

		// TODO display some loader or something ... 
	}, []);

	async function fetchStreamData(creator: string) {
		try {
			let resp = await fetch(config.streamInfoUrl(creator, config.myRegion))

			if (!resp) {
				throw "Stream info fetch result empty ... "
			}

			if (resp.status !== 200) {
				throw resp.text
			}

			let txtData = await resp.text()
			console.log("Stream info fetched: " + txtData)

			let info: StreamInfo = JSON.parse(txtData)

			if (info.media_servers.length == 0) {
				console.log("Stream not available at the moment.")
				return
			}

			console.log("Stream source available.")
			// TODO do some filtering on cnd server or implement fallbacks.
			setStreamSrc(info.media_servers[0].access_url)

		} catch (e) {
			console.log("Failed to fetch stream info: " + e)
			return
		}

	}


	function formPosterUrl(streamer: string | undefined): string {
		return streamer ? config.tnailUrl(streamer) : config.notFoundTnailUrl
	}

	return (
		<div className="streamPlayer">
			<HlsPlayer src={streamSrc}
				posterUrl={formPosterUrl(streamer)}
				shouldPlay={true}
				quality={quality}
				abr={false}
				muted={false} />

			{/* <Chat visible={true} /> */}

			<button onClick={() => setQuality(VideoQuality.HD)}>HD</button>
			<button onClick={() => setQuality(VideoQuality.SD)}>SD</button>
			<button onClick={() => setQuality(VideoQuality.SUBSD)}>SUBSD</button>

		</div>)
}