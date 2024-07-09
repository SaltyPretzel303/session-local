import { useEffect, useState } from "react"
import { MediaServer, StreamInfo } from "../Datas"
import HlsPlayer from "./HlsPlayer"
import config from "../Config"

type StreamPreviewProps = {
	info: StreamInfo
	onClick: (stream: StreamInfo) => void
}

export default function StreamPreview(props: StreamPreviewProps) {

	const [playing, setPlaying] = useState(false)
	const [viewCount, setViewCount] = useState(0)
	let intervalTimer: NodeJS.Timer | undefined = undefined

	useEffect(() => {

		if (intervalTimer || !props.info) {
			return
		}

		loadViews()
		intervalTimer = setInterval(() => loadViews(), 20000)

		return () => {
			if (intervalTimer) {
				clearInterval(intervalTimer)
			}
		}
	})

	async function loadViews(): Promise<void> {
		if (!props.info) {
			return
		}

		let url = config.viewCountUrl(props.info.creator)
		let viewRes = await fetch(url)

		if (!viewRes || viewRes.status != 200) {
			console.log("Failed to fetch view count for: " + props.info.creator)
			return
		}

		setViewCount(Number.parseInt(await viewRes.text()))
	}

	function hoverInHandler() {
		setPlaying(true)
	}

	function hoverOutHandler() {
		setPlaying(false)
	}

	function formStreamUrl(): string | undefined {
		let previewFilter = (s: MediaServer) => s.quality == config.previewQuality
		let mediaServers = props.info.media_servers.filter(previewFilter)

		if (mediaServers.length > 0) {
			return mediaServers[0].access_url
		}

		return undefined
	}


	function formPosterUrl(): string {
		return config.tnailUrl(props.info.creator)
	}

	return (
		<div className='flex flex-col size-full
				px-2
				justify-center 
				rounded-xl
				border-2 border-transparent
				hover:border-2 hover:border-orange-600
				bg-gray-100'
			onMouseEnter={hoverInHandler}
			onMouseLeave={hoverOutHandler}
			onClick={() => props.onClick(props.info)}>

			<p className='ml-4
					justify-center items-center
					font-extrabold text-ellipsis 
					text-[30px]'>
				{props.info.creator}</p>

			<div className='flex size-full 
				justify-center items-center
				border-y border-y-black'>
				<HlsPlayer
					src={formStreamUrl()}
					posterUrl={formPosterUrl()}
					shouldPlay={playing}
					muted={true} />
			</div>

			<div className='flex flex-col w-full p-2'>
				<p className='font-20px font-bold'>{props.info.title}</p>
				<div className='flex flex-row w-full'>
					<p className='flex w-5/6 '>Category: {props.info.category}</p>
					<p className='flex min-w-[80px]
						justify-center
						border border-black rounded-xl 
						px-2 bg-orange-100'>{viewCount}</p>
				</div>


			</div>
		</div>
	)
}