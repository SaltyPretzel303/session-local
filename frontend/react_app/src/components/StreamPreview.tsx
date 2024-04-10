import { useEffect, useState } from "react"
import { StreamInfo } from "../Datas"
import HlsPlayer from "./HlsPlayer"
import config from "../Config"
import { useNavigate } from "react-router-dom"

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

	function formPosterUrl(streamer: string): string {
		return config.tnailUrl(streamer)
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
					src={props.info.media_servers[0].access_url}
					posterUrl={formPosterUrl(props.info.creator)}
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