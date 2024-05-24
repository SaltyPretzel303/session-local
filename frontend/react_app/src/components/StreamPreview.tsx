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
		<div className='flex flex-col size-full
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

			<div className='flex size-full border-y border-y-black'>
				<HlsPlayer
					src={formStreamUrl()}
					posterUrl={formPosterUrl()}
					shouldPlay={playing}
					quality={"subsd"}
					abr={false}
					muted={true} />
			</div>

			<div className='flex flex-col w-full p-2'>
				<p className='font-20px font-bold'>{props.info.title}</p>
				<div className='flex flex-row w-full'>
					<p className='flex w-5/6 '>Category: {props.info.category}</p>
					<p className='flex w-1/6 
						justify-end 
						border border-black rounded-xl 
						px-2 bg-orange-100'>{props.info.viewers}</p>
				</div>


			</div>
		</div>
	)
}