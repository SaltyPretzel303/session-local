import { useState } from "react"
import { MediaServer, StreamInfo } from "../Datas"
import HlsPlayer from "./HlsPlayer"
import config from "../Config"

type StreamPreviewProps = {
	info: StreamInfo
	onClick: (stream: StreamInfo) => void
}

export default function StreamPreview(props: StreamPreviewProps) {

	const [playing, setPlaying] = useState(false)

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
		<div
			onMouseEnter={hoverInHandler}
			onMouseLeave={hoverOutHandler}
			onClick={() => props.onClick(props.info)}
			className='flex flex-row 
				p-2 mx-2 box-border h-40 max-w-96
				border-blue-500 border
				hover:bg-sky-50'
		>

			<div className='h-full w-46'>
				<HlsPlayer
					src={formStreamUrl()}
					posterUrl={formPosterUrl()}
					shouldPlay={playing}
					quality={"subsd"}
					abr={false}
					muted={true} />
			</div>
			<div className='flex flex-col ml-10'>

				<div className='font-extrabold text-nowrap'>
					{props.info.title}</div>

				<div>Creator: {props.info.creator}</div>
				<div>Category: {props.info.category}</div>
				<div>Viewers: {props.info.viewers}</div>

			</div>
		</div>
	)
}