import { useEffect, useState } from "react";
import HlsPlayer from "./components/HlsPlayer";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import { UserInfo } from "./Datas";
import { StreamInfo } from "./Datas";
import config from './Config'

type PlayerPageProps = {
	user: UserInfo | undefined
	getUser: () => Promise<UserInfo | undefined>
	// setLoginVisible: React.Dispatch<boolean>
	// setLoginForced: React.Dispatch<boolean>
}

enum VideoQuality {
	HD = 'hd',
	SD = 'sd',
	SUBSD = 'subsd'
}

export function PlayerPage(props: PlayerPageProps) {

	const { streamer: channel } = useParams<string>()
	const [streamSrc, setStreamSrc] = useState<string | undefined>(undefined)
	const [quality, setQuality] = useState<VideoQuality>(VideoQuality.SUBSD)

	// Data provided using navigate programatically.
	// Mostly from stream preview.
	const { state } = useLocation()

	const navigate = useNavigate()

	useEffect(() => {

		if (!props.user) {
			console.log("Authentication required for this page.")
			// navigate("/", { state: { getUser: props.getUser } })
			navigate("/")
		}

		// This logic is moved in stream preview, that way user can't 
		// navigate to this page if he is not authenticated.

		// props.getUser()
		// 	.then(async (user) => {
		// 		console.log("Obtained user in player page is: " + user)
		// 		if (!user) {
		// 			console.log("Authentication is required for this page.")
		// 			props.setLoginForced(false)
		// 			props.setLoginVisible(true)
		// 		}
		// 	})
		// 	.catch((err) => {
		// 		console.log("Failed to obtain user in playerPage: " + err)
		// 	})

		console.log('Launching player for')
		console.log('\tChannel: ' + channel)
		console.log('\tViewer: ' + props.user?.username)

		if (!channel) {
			console.log("No channel provided.")
			return;
		}

		setupStreamSrc(channel)
			.then(() => {
				console.log("Stream source set, will register viewer.")
				// addViewer() // fire and forget
			})
			.catch((err) => {
				console.log("Failed to set stream source: " + err)
			})

	}, [props.user]);

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

	// async function addViewer() {
	// 	try {
	// 		let res = await fetch(config.addViewerUrl)

	// 		if (!res) {
	// 			throw Error("Http is undefined. ")
	// 		}

	// 		if (res.status != 200) {
	// 			let msg = await res.text
	// 			throw Error("Non 200 code: " + msg)
	// 		}

	// 	} catch (e) {
	// 		console.log("Failed to add viewer: " + e)
	// 	}

	// }

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
			{/* <Chat visible={true} /> */}

			{/* overlay */}
			{/* <div className='relative border border-red-800' >
				<button onClick={() => setQuality(VideoQuality.HD)}>HD</button>
				<button onClick={() => setQuality(VideoQuality.SD)}>SD</button>
				<button onClick={() => setQuality(VideoQuality.SUBSD)}>SUBSD</button>
			</div> */}


		</div>)
}