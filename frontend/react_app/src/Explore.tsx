import PreviewsList from "./components/PreviewList"
import { FollowingInfo, StreamInfo, UserInfo, StreamsOrdering } from "./Datas"
import config from './Config'
import fakeData from './MockupData'
import { useNavigate } from "react-router-dom"
import InfiniteLoader from "react-window-infinite-loader"
import AutoSizer from "react-virtualized-auto-sizer"
import { FixedSizeList as List } from 'react-window'

type ExploreProps = {
	getUser: () => Promise<UserInfo | undefined>
}

export default function Explore(props: ExploreProps) {

	const navigate = useNavigate()

	async function fetchStreamInfo(creator: string):
		Promise<StreamInfo | undefined> {

		let data: StreamInfo | undefined = undefined
		try {
			let res = await fetch(config.streamInfoUrl(creator, config.myRegion))

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

	async function fetchFollowingChannels(username: string):
		Promise<FollowingInfo[]> {

		let data: FollowingInfo[] = []
		try {
			let res = await fetch(config.followingUrl)

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

	async function followingStreamsProvider(start: number, count: number):
		Promise<StreamInfo[]> {

		let user = await props.getUser()

		if (!user) {
			console.log("Failed to fetch following streams, user not found.")
			return []
		}

		let followingChannels = await fetchFollowingChannels(user.username)

		if (!followingChannels) {
			console.log("Following data empty.")
			return []
		}

		let streams: StreamInfo[] = await Promise.all(
			followingChannels
				.map(async f => await fetchStreamInfo(f.following))
				.filter(f => f != undefined) as any
			// offline channels will be undefined 
		)
		console.log("Found: " + streams.length + " live followers.")

		return streams
	}

	async function recommendedStreamsProvider(from: number, count: number):
		Promise<StreamInfo[]> {

		let streams = await fetch(config.allStreamsUrl(from, count, config.myRegion, StreamsOrdering.None))
		if (!streams || streams.status != 200) {
			console.log(`Failed to fetch recommended streams from: ${from}`)
			return []
		}

		let data = await streams.json() as StreamInfo[]

		return data
	}

	async function mockupProvider(start: number, count: number) {
		return fakeData.slice(start, start + count)
	}

	async function emptyProvider(start: number, count: number) {
		return []
	}

	async function exploreStreamsProvider(from: number, count: number)
		: Promise<StreamInfo[]> {

		return []
	}

	async function allProvider(from: number,
		count: number,
		ordering: StreamsOrdering)

		: Promise<StreamInfo[]> {

		let url = config.allStreamsUrl(from, count, config.myRegion, ordering)
		try {
			let response = await fetch(url)
			if (response.status != 200) {
				let msg = "Returned non 200 code: " + response.status
				let data = await response.text()

				if (data) {
					msg += "\nMsg: " + data
				}

				throw Error(msg)
			}

			return await response.json() as StreamInfo[]

		} catch (e) {
			console.log("Failed to fetch all streams: " + e)
			return []
		}
	}

	async function streamClickHandler(stream: StreamInfo) {
		let user = await props.getUser()
		if (!user) {
			console.log("Authenticate to open player page.")
			// TODO show some popup message or something
			return
		}

		console.log("Will navigate to watch: " + stream.creator)
		navigate("/watch/" + stream.creator, { state: { streamData: stream } })
	}

	return (
		<div className='w-full h-full flex flex-row justify-center p-4'>

			<div className='flex h-full w-1/3 items-center'>
				<PreviewsList title="Following"
					streamClickHandler={streamClickHandler}
					streamsProvider={mockupProvider} />
			</div>

			<div className='flex h-full w-1/4 items-center mx-5' >
				<PreviewsList title="Categories"
					streamClickHandler={streamClickHandler}
					streamsProvider={mockupProvider} />
			</div>

			<div className='flex h-full w-1/3 items-center'>
				<PreviewsList title="Random"
					streamClickHandler={streamClickHandler}
					streamsProvider={mockupProvider} />
			</div>

		</div>
	)

}