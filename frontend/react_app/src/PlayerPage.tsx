import { useEffect, useState } from "react";
import HlsPlayer from "./components/HlsPlayer";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import { UserInfo } from "./Datas";
import { StreamInfo } from "./Datas";
import config from './Config'
import Chat from "./components/Chat";


type PlayerPageProps = {
	getUser: () => Promise<UserInfo | undefined>
}

enum VideoQuality {
	HD = 'hd',
	SD = 'sd',
	SUBSD = 'subsd'
}

function Overlay(
	{
		stream,
		chatVisible,
		setChatVisible,
		visible,
		setOverlayVisible
	}: {
		stream: StreamInfo | undefined,
		chatVisible: boolean,
		setChatVisible: React.Dispatch<React.SetStateAction<boolean>>,
		visible: boolean,
		setOverlayVisible: React.Dispatch<React.SetStateAction<boolean>>
	}) {

	const [views, setViews] = useState(0)
	const [intervalTimer, setIntervalTimer] = useState<NodeJS.Timer | undefined>(undefined)
	const [hideTimeout, setHideTimeout] = useState<NodeJS.Timeout | undefined>(undefined)

	useEffect(() => {
		if (visible) {
			setIntervalTimer(setInterval(() => loadViews(), 10000))

			clearTimeout(hideTimeout)
			setHideTimeout(setTimeout(() => setOverlayVisible(false), 3000))
		} else {
			clearInterval(intervalTimer)
			clearTimeout(hideTimeout)
		}

		return () => {
			clearInterval(intervalTimer)
			clearTimeout(hideTimeout)
		}
	}, [visible])

	async function loadViews(): Promise<void> {
		if (!stream) {
			return
		}

		let url = config.viewCountUrl(stream.creator)
		let view_res = await fetch(url)

		if (!view_res || view_res.status != 200) {
			console.log("Failed to fetch views count.")
			return
		}

		setViews(Number.parseInt(await view_res.text()))
	}


	return (
		<div className='flex size-full absolute
			pointer-events-none'>


			<div className='flex flex-row 
				justify-center items-center
				w-full h-[100px] 
				px-4
				bg-gradient-to-b from-slate-400 to-transparent'>

				<div className='flex flex-col h-full w-full pt-4'>
					<p className='text-[30px] text-black'>{stream?.title}</p>
					<div className='flex flex-row items-baseline'>
						<p className='text-[14px] text-black'>by:</p>
						<p className='text-[20px] text-black ml-2'>{stream?.creator}</p>

						<p className='text-[14px] text-black ml-20'>watching:</p>
						<p className='text-[20px] text-black ml-2'>{views}</p>
					</div>
				</div>

				<button className='flex w-[130px] 
					border rounded-xl 
					mb-6
					justify-center
					text-[20px]
					pointer-events-auto
					hover:border hover:border-orange-500'
					onClick={() => setChatVisible(!chatVisible)}>
					{chatVisible ? "Hide chat" : "Show chat"}
				</button>
			</div>
		</div>
	)
}

export function PlayerPage(props: PlayerPageProps) {

	const { channel } = useParams<string>()
	const [stream, setStream] = useState<StreamInfo | undefined>(undefined)
	const [streamSrc, setStreamSrc] = useState<string | undefined>(undefined)
	const [quality, setQuality] = useState<VideoQuality>(VideoQuality.SUBSD)
	const [overlayVisible, setOverlayVisible] = useState(true)
	const [chatVisible, setChatVisible] = useState(true)

	// Data provided using navigate programatically.
	// Mostly from stream preview.
	const { state } = useLocation()

	const navigate = useNavigate()

	useEffect(() => {
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


			<div className='flex relative size-full
					justify-center items-center'
				onMouseMove={() => setOverlayVisible(true)}
				onMouseEnter={() => setOverlayVisible(true)}
				onMouseLeave={() => setOverlayVisible(false)}>

				<HlsPlayer
					src={streamSrc}
					posterUrl={formPosterUrl(channel)}
					shouldPlay={true}
					quality={quality}
					abr={false}
					muted={false}
					onDone={doneHandler} />

				{overlayVisible && <Overlay stream={stream}
					chatVisible={chatVisible}
					setChatVisible={setChatVisible}
					visible={overlayVisible}
					setOverlayVisible={setOverlayVisible} />}
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