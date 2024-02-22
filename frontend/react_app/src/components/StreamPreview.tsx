import { useEffect, useState } from "react"
import { StreamInfo } from "../dataModel/StreamInfo"
import HlsPlayer from "./HlsPlayer"

type StreamPreviewProps = {
	info: StreamInfo
}

export default function StreamPreview(props: StreamPreviewProps) {
	const focusedBorder = "3px solid white"
	const normalBorder = "1px solid gray"

	const [playing, setPlaying] = useState(false)
	const [border, setBorder] = useState(normalBorder)

	function hoverIn() {
		setPlaying(true)
		setBorder(focusedBorder)
	}

	function hoverOut() {
		setPlaying(false)
		setBorder(normalBorder)
	}

	// TODO move to config
	function formPosterUrl(streamer: string): string {
		// return 'http://stream-registry.session:8002/tnail/' + streamer
		return 'http://localhost:8002/tnail/' + streamer

	}

	return (
		<div
			onMouseEnter={hoverIn}
			onMouseLeave={hoverOut}
			style={
				{
					display: "flex",
					flexDirection: "row",
					boxSizing: "border-box",
					margin: "10px",
					padding: "10px",
					width: "400px",
					minWidth: "200px",
					// height: "100%",
					border: `${border}`
				}
			}>

			<HlsPlayer
				src={props.info.media_server.full_path}
				posterUrl={formPosterUrl(props.info.creator)}
				shouldPlay={playing}
				quality={"subsd"}
				abr={false}
				muted={true} />

			<div style={
				{
					display: "flex",
					flexDirection: "column",
					marginLeft: "10px"
				}
			}>

				<div>{props.info.title}</div>
				<div>{props.info.creator}</div>
				<div>{props.info.category}</div>
				<div>{props.info.viewers}</div>
			</div>
		</div>
	)
}