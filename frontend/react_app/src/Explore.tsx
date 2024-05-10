import { FollowingInfo, StreamInfo, UserInfo, OrderingOption, Orderings } from "./Datas"
import config from './Config'
import fakeData from './MockupData'
import { useNavigate } from "react-router-dom"
import StreamPreview from "./components/StreamPreview"
import GenericPreviewList from "./components/GenericPreviewList"
import { useState } from "react"
import { setCookie } from "react-use-cookie"

type ExploreProps = {
	getUser: () => Promise<UserInfo | undefined>
}

export default function Explore(props: ExploreProps) {

	const navigate = useNavigate()

	const followingOrders: OrderingOption[] = [
		{ displayName: "Viewers high", value: Orderings.viewsDescending },
		{ displayName: "Viewers low", value: Orderings.recommendedAscending }
	]
	const [followingOrder, setFollowingOrder] = useState<Orderings>(followingOrders[0].value)
	function selectFollowOrdering(e: React.ChangeEvent<HTMLSelectElement>) {
		setFollowingOrder(Orderings[e.target.value as keyof typeof Orderings])
	}

	const exploreOrders: OrderingOption[] = [
		{ displayName: "Viewers high", value: Orderings.viewsDescending },
		{ displayName: "Viewers low", value: Orderings.recommendedAscending }
	]
	const [exploreOrder, setExploreOrder] = useState<Orderings>(exploreOrders[0].value)
	function selectExploreOrdering(e: React.ChangeEvent<HTMLSelectElement>) {
		setFollowingOrder(Orderings[e.target.value as keyof typeof Orderings])
	}

	const categoryOrders: OrderingOption[] = [
		{ displayName: "Viewers high", value: Orderings.viewsDescending },
		{ displayName: "Viewers low", value: Orderings.viewsAscending },
		{ displayName: "Popular high", value: Orderings.popularityDescending },
		{ displayName: "Popular low", value: Orderings.popularityAscending }
	]
	const [categoryOrder, setCategoryOrder] = useState<Orderings>(categoryOrders[0].value)
	function selectCategoryOrdering(e: React.ChangeEvent<HTMLSelectElement>) {
		setFollowingOrder(Orderings[e.target.value as keyof typeof Orderings])
	}

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

	async function mockupProvider(start: number, to: number) {
		let data = []
		for (let i = start; i < to; i++) {
			data.push(
				{
					"title": "title_" + i,
					"creator": "streamer-0",
					"category": "chatting",
					"viewers": 10,
					"media_servers": [
						{
							"quality": "preview",
							"access_url": "http://eu-0-cdn.session.com/preview/streamer-0/index.m3u8"
						}
					]
				}
			)
		}
		return data
	}

	async function allProvider(start: number, end: number): Promise<StreamInfo[]> {

		let url = config.allStreamsUrl(start, end, config.myRegion, followingOrder)

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

	function streamRenderer(stream: StreamInfo): JSX.Element {
		return (
			<StreamPreview
				info={stream}
				onClick={streamClickHandler} />
		)
	}

	function categoryRenderer(category: string) {
		return (
			<div className='flex flex-col w-full h-full
				text-black text-[30px]
				p-4'>

				<img className='flex w-full h-full' src={config.lowCategoryIconUrl(category)}></img>
				<p>{category}</p>

			</div>
		)
	}

	async function getCategories(f: number, t: number): Promise<string[]> {

		try {
			let res = await fetch(config.categoriesRangeUrl(f, t))

			if (res.status != 200) {
				throw Error("Status code: " + res.status)
			}

			return await res.json() as string[]
		} catch (e) {
			console.log("Failed to load categories: " + e)
			return []
		}
	}

	return (
		<div className='flex flex-row 
			size-full 
			justify-center items-center 
			p-4'>

			<div className='flex flex-col 
				h-full w-[600px] min-w-[600px]
				items-center p-4
				bg-sky-900'>

				<p className='text-[30px]'>Following</p>
				<div className='flex flex-row-reverse w-full h-[50px] mt-2'>
					<select className='rounded-lg px-2 bg-transparent border border-sky-950'
						defaultValue={followingOrders[0].value}
						onChange={selectFollowOrdering}>
						{
							followingOrders.map((o) =>

								<option
									key={o.value}
									value={o.value}>

									{o.displayName}
								</option>
							)
						}
					</select>
				</div>
				<GenericPreviewList<StreamInfo>
					dataProvider={allProvider}
					renderItem={streamRenderer}
					itemSize={300}
				/>
			</div>

			<div className='flex flex-col items-center 
				h-[80%] w-[200px] min-w-[200px]
				mx-20 
				bg-sky-900
				max-[1630px]:hidden'>

				<p>Categories</p>
				<div className='flex flex-row justify-center w-full h-[50px] mt-2'>
					<select className='rounded-lg p-2 bg-transparent border border-sky-950'
						defaultValue={categoryOrders[0].value}
						onChange={selectCategoryOrdering}>
						{
							categoryOrders.map((o) =>

								<option
									key={o.value}
									value={o.value}>

									{o.displayName}
								</option>
							)
						}
					</select>
				</div>
				<GenericPreviewList<string>
					dataProvider={getCategories}
					renderItem={categoryRenderer}
					itemSize={220}
				/>

			</div>

			<div className='flex flex-col
			 	h-full w-[600px] min-w-[600px]
				items-center p-4
				bg-sky-900
				max-[1630px]:ml-4
				max-[1200px]:hidden'>

				<p className='text-[30px]'>Explore</p>
				<div className='flex flex-row-reverse w-full h-[50px] mt-2'>
					<select className='rounded-lg p-2 bg-transparent border border-sky-950'
						defaultValue={exploreOrders[0].value}
						onChange={selectExploreOrdering}>
						{
							exploreOrders.map((o) =>

								<option
									key={o.value}
									value={o.value}>

									{o.displayName}
								</option>
							)
						}
					</select>
				</div>
				<GenericPreviewList<StreamInfo>
					dataProvider={allProvider}
					renderItem={streamRenderer}
					itemSize={300}
				/>
			</div>

		</div>
	)

}

