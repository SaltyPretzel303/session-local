import "../style/PreviewContainer.css"
import "../style/PreviewsList.css"
import { StreamInfo } from "../data_model/StreamInfo"
import { StreamPreview } from "./StreamPreview"

export interface PreviewsContainerProps {
	title: string
	streams: StreamInfo[]
}

export function PreviewsContainer(props: PreviewsContainerProps) {

	return (
		<div className="previewsContainer">
			<h1>{props.title}</h1>
			<div className="previewsList">
				{
					props.streams.map((stream) => {
						return (
							<StreamPreview stream={stream} thumbnail={undefined} key={stream.creator} />
						)
					})
				}
			</div>
		</div>
	)

}