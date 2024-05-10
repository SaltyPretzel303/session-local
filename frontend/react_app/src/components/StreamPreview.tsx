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
				h-full
				w-full
				box-border p-2
				justify-center
				border-2 border-sky-900
				hover:border-2 hover:border-sky-800'>

			<div className='flex h-full w-2/3 mr-4 '>
				<HlsPlayer
					src={formStreamUrl()}
					posterUrl={formPosterUrl()}
					shouldPlay={playing}
					quality={"subsd"}
					abr={false}
					muted={true} />
			</div>
			<div className='flex flex-col h-full w-1/3'>

				<div className='font-extrabold text-nowrap'>
					{props.info.title}</div>

				<div>Creator: {props.info.creator}</div>
				<div>Category: {props.info.category}</div>
				<div>Viewers: {props.info.viewers}</div>

			</div>
		</div>
	)
}