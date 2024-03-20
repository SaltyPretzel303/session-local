import PreviewsList from "./components/PreviewList"
import { FollowingInfo, StreamInfo, UserInfo } from "./Datas"
import streams from "./StreamData"
import config from './Config'

type ExploreProps = {
	getUser: () => Promise<UserInfo | undefined>
}

export default function Explore(props: ExploreProps) {

	async function fetchStream(creator: string): Promise<StreamInfo | undefined> {

		let data: StreamInfo | undefined = undefined
		try {
			let res = await fetch(config.streamInfoUrl(creator, config.region))

			if (res.status != 200) {
				throw Error(`Status: ${res.status} msg: ${await res.text()}`)
			}

			data = await res.json()
		} catch (e) {
			console.log("Fetch stream info failed: " + e)
			// data stays undefined
		}

		return data
	}

	async function fetchFollowing(username: string): Promise<FollowingInfo[]> {
		let data: FollowingInfo[] = []

		try {
			let res = await fetch(config.followingUrl(username))
			
			if (res.status != 200) {
				throw Error(`Status: ${res.status} msg: ${await res.text()}.`)
			}

			data = await res.json()
		} catch (e) {
			console.log("Failed to fetch following records: " + e)
			// data stays undefined
		}

		return data
	}

	async function followingStreamsProvider(start: number, count: number): Promise<StreamInfo[]> {
		console.log(`Requested following streams from: ${start} cnt: ${count}`)

		let user = await props.getUser()

		if (!user) {
			console.log("Failed to fetch following streams, user not found.")
			return []
		}

		let following_data = await fetchFollowing(user.username)

		if (!following_data) {
			console.log("Following data empty.")
			return []
		}

		let streams: StreamInfo[] = await Promise.all(
			following_data
				.map(async f => await fetchStream(f.following))
				.filter(f => f != undefined) as any
			// offline streams will be undefined
		)
		console.log("Found: " + streams.length + " live followers.")

		return streams
	}

	async function recommendedStreamsProvider(from: number, count: number): Promise<StreamInfo[]> {
		let streams = await fetch("http://session.com/stream/all")
		let data = await streams.json() as StreamInfo[]

		console.log("Reccommended streams: ")
		console.log(data)

		return data
	}

	async function exploreStreamsProvider(from: number, count: number): Promise<StreamInfo[]> {
		return []
		console.log(`Returning explore: ${from} - ${count}`)
		return streams.slice(from, from + count)
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
			<PreviewsList title={"Recommended"} streamsProvider={recommendedStreamsProvider} />
			<PreviewsList title={"Explore"} streamsProvider={exploreStreamsProvider} />

		</div >)

}