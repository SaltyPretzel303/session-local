import { useEffect, useState } from "react";
import HlsPlayer from "./components/HlsPlayer";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import { UserInfo } from "./Datas";
import { StreamInfo } from "./Datas";
import config from './Config'
import Chat from "./components/Chat";
import StreamOverlay from "./components/StreamOverlay";


type PlayerPageProps = {
	getUser: () => Promise<UserInfo | undefined>
}

export function PlayerPage(props: PlayerPageProps) {

	const { channel } = useParams<string>()
	const [stream, setStream] = useState<StreamInfo | undefined>(undefined)
	const [streamSrc, setStreamSrc] = useState<string | undefined>(undefined)
	const [overlayVisible, setOverlayVisible] = useState(false)
	const [chatVisible, setChatVisible] = useState(true)

	// Data provided using navigate programatically.
	// Mostly from stream preview.
	const { state } = useLocation()

	const navigate = useNavigate()

	useEffect(() => {
		console.log("Creating player page.")
		if (channel == undefined || channel == "") {
			return
		}

		loadData()

	}, [channel]);

	async function loadData() {
		let user = await props.getUser()

		if (!user) {
			console.log("Authentication required for this page.")
			navigate("/")

			return
		}

		console.log('Launching player for: ')
		console.log('\tChannel: ' + channel)
		console.log('\tViewer: ' + user?.username)

		if (!channel) {
			console.log("No channel provided.")
			return;
		}

		let streamInfo = await loadStreamData(channel)
		setStream(streamInfo)

		if (streamInfo && streamInfo.media_servers.length > 0) {
			setStreamSrc(streamInfo.media_servers[0].access_url)
		}
	}

	async function loadStreamData(creator: string): Promise<StreamInfo | undefined> {
		if (state) {
			console.log("Stream data provided.")

			const { streamData }: { streamData: StreamInfo } = state

			return streamData
		} else {
			console.log("Will fetch stream data.")

			return await fetchStreamData(creator)
		}

	}

	async function fetchStreamData(creator: string): Promise<StreamInfo | undefined> {
		try {
			let resp = await fetch(config.streamInfoUrl(creator, config.myRegion))

			if (resp.status !== 200) {
				throw "Return status: " + resp.status
			}

			return await resp.json()
		} catch (e) {
			console.log("Failed to fetch stream info: " + e)
			return undefined
		}

	}

	function formPosterUrl(streamer: string | undefined): string {
		return streamer ? config.tnailUrl(streamer) : config.notFoundTnailUrl
	}

	function doneHandler() {
		console.log("Handling stream done in playerPage.")
	}

	return (
		<div className='flex flex-row size-full
			justify-center items-center 
			bg-slate-900'>


			<div className='flex relative 
					size-full
					justify-center items-center'

				onMouseEnter={() => setOverlayVisible(true)}
				onMouseLeave={() => setOverlayVisible(false)}>

				<HlsPlayer
					src={streamSrc}
					posterUrl={formPosterUrl(channel)}
					shouldPlay={true}
					muted={false}
					onDone={doneHandler} />

				<StreamOverlay
					stream={stream}
					chatVisible={chatVisible}
					setChatVisible={setChatVisible}
					visible={overlayVisible}
				/>
			</div>

			{channel && chatVisible &&
				<div className='flex flex-col
				h-full w-[300px] 
				pt-2
				justify-end items-center
				text-lg text-white
				'>
					<Chat
						channel={channel}
						getUser={props.getUser} />
				</div>
			}



		</div >
	)
}