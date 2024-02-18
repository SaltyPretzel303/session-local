import PreviewsList from "./components/PreviewList"
import { StreamInfo } from "./dataModel/StreamInfo"
import streams from "./Data"

type ExploreProps = {

}

export default function Explore(props: ExploreProps) {

	async function followingStreamsProvider(from: number, to: number): Promise<StreamInfo[]> {
		console.log(`Returning following: ${from} - ${to}`)
		return streams.slice(from, to)
	}
	async function recommendedStreamsProvider(from: number, to: number): Promise<StreamInfo[]> {
		console.log(`Returning recommended: ${from} - ${to}`)
		return streams.slice(from, to)
	}
	async function exploreStreamsProvider(from: number, to: number): Promise<StreamInfo[]> {
		console.log(`Returning explore: ${from} - ${to}`)
		return streams.slice(from, to)
	}

	return (
		<div style={
			{
				width: "100%",
				height: "100%",
				boxSizing: "border-box",
				border: "2px solid red",
				padding: "10px",
				display: "flex",
				flexDirection: "column",
				backgroundColor: "black",
				// padding: "5px"
			}
		}>

			<PreviewsList title={"Following"} streamsProvider={followingStreamsProvider} />
			{/* <PreviewsList title={"Recommended"} streamsProvider={recommendedStreamsProvider} />
			<PreviewsList title={"Explore"} streamsProvider={exploreStreamsProvider} /> */}

		</div >)

}