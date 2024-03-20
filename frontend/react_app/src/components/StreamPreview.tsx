import { useEffect, useState } from "react"
import { StreamInfo } from "../Datas"
import HlsPlayer from "./HlsPlayer"
import config from "../Config"

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

	function formPosterUrl(streamer: string): string {
		return config.tnailUrl(streamer)
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
				src={props.info.media_servers[0].access_url}
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

				<div style={{ fontWeight: 'bolder' }}>{props.info.title}</div>
				<div>Creator: {props.info.creator}</div>
				<div>Category: {props.info.category}</div>
				<div>Viewers: {props.info.viewers}</div>
			</div>
		</div>
	)
}