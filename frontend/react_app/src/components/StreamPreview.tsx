import { Navigate, useNavigate } from "react-router-dom";
import { StreamInfo } from "../data_model/StreamInfo";
import "../style/StreamPreview.css"
const logo = require('../thumbnail.jpeg');

export interface StreamPreviewProps {
	stream: StreamInfo
	// streamer: string
	// title: string
	// viewers: number
	thumbnail: ImageBitmap | undefined
	// category 
}

export function StreamPreview(props: StreamPreviewProps) {

	const navigate = useNavigate()

	function streamClick() {
		navigate('/watch/streamer')
	}

	return (
		<div className="streamPreview" onClick={streamClick}>
			<img src={String(logo)} />
			<div className="infoContainer">
				<p className="title">{props.stream.title}</p>
				<p className="streamer">{props.stream.creator}</p>
				<p className="viewers">{props.stream.viewers}</p>
			</div>
		</div>
	)
}