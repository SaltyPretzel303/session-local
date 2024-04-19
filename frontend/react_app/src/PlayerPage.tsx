import { useEffect, useState } from "react";
import HlsPlayer from "./components/HlsPlayer";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import { UserInfo } from "./Datas";
import { StreamInfo } from "./Datas";
import config from './Config'

type PlayerPageProps = {
	getUser: () => Promise<UserInfo | undefined>
}

enum VideoQuality {
	HD = 'hd',
	SD = 'sd',
	SUBSD = 'subsd'
}

export function PlayerPage(props: PlayerPageProps) {

	// const { streamer: channel } = useParams<string>()
	const { channel } = useParams<string>()
	const [streamSrc, setStreamSrc] = useState<string | undefined>(undefined)
	const [quality, setQuality] = useState<VideoQuality>(VideoQuality.SUBSD)
	const [viewsCount, setViewsCount] = useState("0")

	// Data provided using navigate programatically.
	// Mostly from stream preview.
	const { state } = useLocation()

	const navigate = useNavigate()

	useEffect(() => {

		props.getUser()
			.then((user) => {
				if (!user) {
					console.log("Authentication required for this page.")
					navigate("/")
					return // is it necessary ?
				}

				console.log('Launching player for: ')
				console.log('\tChannel: ' + channel)
				console.log('\tViewer: ' + user?.username)

				if (!channel) {
					console.log("No channel provided.")
					return;
				}

				setupStreamSrc(channel)
					.then(() => {
						console.log("Stream source set.")
					})
					.catch((err) => {
						console.log("Failed to set stream source: " + err)
					})

			})
			.catch((err) => {

			})

	}, []);

	async function setupStreamSrc(creator: string) {
		if (state) {
			console.log("Stream data provided.")

			const { streamData }: { streamData: StreamInfo } = state
			setStreamSrc(streamData.media_servers[0].access_url)
		} else {
			console.log("Will fetch stream data.")

			fetchStreamData(creator)
		}
	}

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

	async function loadViewsHandler() {
		console.log("Will load views counter")
		if (!channel) {
			return
		}
		let url = config.viewCountUrl(channel)
		let view_res = await fetch(url)

		if (!view_res || view_res.status != 200) {
			console.log("Failed to fetch views count.")
			return
		}

		let value = await view_res.text()
		console.log(`viewers_count: ${value}`)

		setViewsCount(value)
	}

	function formPosterUrl(streamer: string | undefined): string {
		return streamer ? config.tnailUrl(streamer) : config.notFoundTnailUrl
	}

	function doneHandler() {
		console.log("Handling stream done in playerPage.")
	}

	return (
		<div className='w-full h-full'>
			<div className='w-full h-full
				box-border
				'>
				<HlsPlayer src={streamSrc}
					posterUrl={formPosterUrl(channel)}
					shouldPlay={true}
					quality={quality}
					abr={false}
					muted={false}
					onDone={doneHandler} />
			</div>
			<div className='flex-row'>
				<p>
					{viewsCount}
				</p>
				<button onClick={loadViewsHandler}>Load views</button>
			</div>
			{/* <Chat visible={true} /> */}

			{/* overlay */}
			{/* <div className='relative border border-red-800' >
				<button onClick={() => setQuality(VideoQuality.HD)}>HD</button>
				<button onClick={() => setQuality(VideoQuality.SD)}>SD</button>
				<button onClick={() => setQuality(VideoQuality.SUBSD)}>SUBSD</button>
			</div> */}


		</div>)
}