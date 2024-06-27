import { FollowingInfo, StreamInfo, UserInfo, OrderingOption, Orderings, Category } from "./Datas"
import config from './Config'
import { useNavigate } from "react-router-dom"
import StreamPreview from "./components/StreamPreview"
import GenericPreviewList from "./components/GenericLazyList"
import { Dispatch, SetStateAction, useEffect, useState } from "react"
import SortSelector from "./components/SortSelector"


type ExploreProps = {
	getUser: () => Promise<UserInfo | undefined>
}

export default function Explore(props: ExploreProps) {

	const navigate = useNavigate()

	// #region ORDERS
	const followingOrders: OrderingOption[] = [
		{ displayName: "Viewers high", value: Orderings.viewsDescending },
		{ displayName: "Viewers low", value: Orderings.viewsAscending }
	]
	const [selectedFollowingOrder, setSelectedFollowingOrder]
		= useState<Orderings>(followingOrders[0].value)

	const categoryOrders: OrderingOption[] = [
		{ displayName: "Viewers high", value: Orderings.viewsDescending },
		{ displayName: "Viewers low", value: Orderings.viewsAscending },
		{ displayName: "Popular high", value: Orderings.popularityDescending },
		{ displayName: "Popular low", value: Orderings.popularityAscending }
	]
	const [selectedCategoryOrder, setSelectedCategoryOrder]
		= useState<Orderings>(categoryOrders[0].value)

	const exploreOrders: OrderingOption[] = [
		{ displayName: "Viewers high", value: Orderings.viewsDescending },
		{ displayName: "Viewers low", value: Orderings.viewsAscending }
	]
	const [selectedExploreOrder, setSelectedExploreOrder]
		= useState<Orderings>(exploreOrders[0].value)

	// #endregion 

	// #region ORDER SELECTORS
	function selectFollowOrdering(e: React.ChangeEvent<HTMLSelectElement>) {
		setSelectedFollowingOrder(Orderings[e.target.value as keyof typeof Orderings])
	}

	function selectExploreOrdering(e: React.ChangeEvent<HTMLSelectElement>) {
		setSelectedExploreOrder(Orderings[e.target.value as keyof typeof Orderings])
	}

	function selectCategoryOrdering(e: React.ChangeEvent<HTMLSelectElement>) {
		setSelectedCategoryOrder(Orderings[e.target.value as keyof typeof Orderings])
	}
	// #endregion

	// #region ITEMS

	const [selectedCategory, setSelectedCategory]
		= useState<Category | undefined>(undefined)

	const [followingStreams, setFollowingStreams] = useState<StreamInfo[]>([])
	const [hasMoreFollowingStreams, setHasMoreFollowingStreams] =
		useState<boolean>(true)

	const [categories, setCategories] = useState<Category[]>([])
	const [hasMoreCategories, setHasMoreCategories] = useState<boolean>(true)

	const [exploreStreams, setExploreStreams] = useState<StreamInfo[]>([])
	const [hasMoreExploreStreams, setHasMoreExpoloreStreams] =
		useState<boolean>(true)

	// #endregion 

	async function itemsProvider<T>(start: number,
		end: number,
		items: T[],
		setItems: React.Dispatch<React.SetStateAction<T[]>>,
		setHasMoreItems: React.Dispatch<React.SetStateAction<boolean>>,
		fetchItems: (f: number, c: number, ordering: Orderings) => Promise<T[]>,
		sort: Orderings): Promise<void> {

		let newItems = await fetchItems(start, end - start, sort)
		setItems(items.concat(newItems))
		setHasMoreItems(newItems.length == end - start)

		return
	}

	// #region FETCH METHODS

	async function fetchCategoryStreams(start: number,
		count: number,
		category: string | undefined,
		sort: Orderings): Promise<StreamInfo[]> {

		console.log("Fetching stream for cat: " + category)
		if (!category) {
			return []
		}

		try {
			let url = config.categoryStreamsUrl(category,
				start,
				count,
				config.myRegion)

			let res = await fetch(url, { method: "GET" })
			if (res.status != 200) {
				throw Error("Non 200 status code: " + res.status)
			}

			let newData = await res.json() as StreamInfo[]
			console.log(`count for: ${category} -> ${newData.length}`)

			return newData
		} catch (e) {
			console.log("Failed to fetch streams for: " + category + ", err: " + e)
			return []
		}
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

	async function fetchFollowingChannels(start: number, count: number):
		Promise<FollowingInfo[]> {

		let data: FollowingInfo[] = []
		try {
			let res = await fetch(config.followingUrl(start, count, selectedFollowingOrder))

			if (res.status != 200) {
				throw Error(`Status: ${res.status} msg: ${await res.text()}.`)
			}

			data = await res.json() as FollowingInfo[]
		} catch (e) {
			console.log("Failed to fetch following records: " + e)
			// data stays undefined
		}

		return data
	}

	async function fetchFollowingStreams(start: number, count: number, sort: Orderings): Promise<StreamInfo[]> {
		let followingChannels = await fetchFollowingChannels(start, count)

		return await Promise.all(followingChannels
			.map(async f => await fetchStreamInfo(f.following))
			.filter(f => f != undefined)) as StreamInfo[]
	}

	async function fetchMockupData(start: number, count: number): Promise<StreamInfo[]> {
		return new Array(count).fill(null).map((el, i) => {
			let ind = start + i
			return {
				"title": "title_" + ind,
				"creator": "streamer-0",
				"category": "chatting",
				"viewers": 2 + ind + 3,
				"media_servers": [
					{
						"quality": "preview",
						"access_url": "http://eu-0-cdn.session.com/preview/streamer-0/index.m3u8"
					}
				]
			}
		})
	}

	async function fetchAllStreams(start: number, count: number, order: Orderings): Promise<StreamInfo[]> {
		let url = config.allStreamsUrl(start, count, config.myRegion, order)

		try {
			let response = await fetch(url)
			if (response.status != 200) {
				throw Error("Returned non 200 code: " + response.status)
			}

			return await response.json() as StreamInfo[]

		} catch (e) {
			console.log("Failed to fetch all streams: " + e)
			return []
		}
	}

	async function fetchRecommendedStreams(start: number, count: number, sort: Orderings): Promise<StreamInfo[]> {
		// TODO do some backand magic 
		return fetchMockupData(start, count)
	}

	async function fetchCategories(start: number, count: number, sort: Orderings): Promise<Category[]> {
		try {
			let res = await fetch(config.categoriesRangeUrl(start, count))

			if (res.status != 200) {
				throw Error("Status code: " + res.status)
			}

			return await res.json() as Category[]
		} catch (e) {
			console.log("Failed to load categories: " + e)
			return []
		}
	}

	// #endregion

	// #region RENDERERES

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
		return <StreamPreview info={stream} onClick={streamClickHandler} />
	}

	function loadingStreamRenderer(): JSX.Element {
		return <div className='flex size-full 
			justify-center items-center
			rounded-xl
			border border-black 
			bg-gray-200 
			text-[30px]'>Loading ... </div>
	}

	function categoryRenderer(category: Category) {
		return (
			<div className='flex flex-col 
					size-full p-2 mx-2
					text-center text-black text-[25px]
					rounded-xl
					bg-slate-700
					border-2 border-transparent
					hover:border-2 hover:border-sky-800'
				onClick={() => categoryClick(category)}>

				<img className='flex size-full'
					src={config.lowCategoryIconUrl(category.name)} />
				<p className='flex w-full 
					border-2 border-black 
					rounded-xl
					justify-center'>{category.display_name}</p>

			</div>
		)
	}

	function loadingCategoryRendered(): JSX.Element {
		return <div className='flex size-full 
			justify-center items-center
			text-[30px] text-black'> Loading </div>
	}

	function categoryClick(category: Category) {
		console.log("Selecting category: " + category.name)

		setSelectedCategory(category)
		setExploreStreams([])
		setHasMoreExpoloreStreams(true)

		console.log("Selection done.")
	}

	// #endregion 

	return (
		<div className='flex flex-row  size-full 
			justify-center items-center 
			font-[Oswald]
			bg-gradient-to-b from-slate-900 from-60% to-slate-800
			pt-4
			'>

			{/* FOLLOWING */}
			<div className='flex flex-col items-center 
				h-full
				px-4
				'>

				<div className='flex flex-row w-full 
					px-4 mb-2
					justify-start items-center'>

					<p className='flex w-3/4 text-[30px] text-orange-500'>Following</p>

					<div className='flex flex-row-reverse w-1/4 h-[50px] mt-2 '>

						<SortSelector
							values={followingOrders}
							onSelect={(o) => setSelectedFollowingOrder(o)}
						/>

					</div>
				</div>
				<div className='flex flex-col 
					w-[700px] min-w-[400px] h-full'>

					<GenericPreviewList<StreamInfo>
						items={followingStreams}
						itemsProvider={async (f: number, t: number) =>
							itemsProvider(f, t,
								followingStreams,
								setFollowingStreams,
								setHasMoreFollowingStreams,
								fetchAllStreams,
								selectedFollowingOrder)
						}
						hasMoreData={hasMoreFollowingStreams}
						renderItem={streamRenderer}
						renderLoading={loadingStreamRenderer}
						relativeHeight={75}
					/>
				</div>
			</div>

			{/* RIGHT SECTION  */}
			<div className="flex flex-row h-full 
				justify-end items-center
				ml-[100px] mb-4
				border-4 border-slate-800
				rounded-2xl
				">

				{/* CATEGORIES */}
				<div className='flex flex-col 
						h-[90%] w-[170px]
						justify-center items-center
						bg-gradient-to-b from-slate-700 from-20% to-slate-800
						rounded-2xl 
						pt-2 ml-14
						'>

					<SortSelector
						values={categoryOrders}
						onSelect={(o) => setSelectedCategoryOrder(o)}
					/>

					<GenericPreviewList<Category>
						items={categories}
						itemsProvider={async (f: number, t: number) =>
							itemsProvider(f, t,
								categories,
								setCategories,
								setHasMoreCategories,
								fetchCategories,
								selectedCategoryOrder)
						}
						hasMoreData={hasMoreCategories}
						renderItem={categoryRenderer}
						renderLoading={loadingCategoryRendered}
						relativeHeight={100}
					/>

				</div>

				{/* EXPLORE */}
				<div className='flex flex-col items-center
						h-full w-[700px] min-w-[700px]
						px-4 ml-4'>

					<div className='flex flex-row w-full 
							px-4 mb-2 
							justify-start items-center'>

						<p className='flex flex-row w-3/4 text-[30px] text-orange-500 '>
							{selectedCategory ? selectedCategory.display_name : "Recommended"}
						</p>

						<div className='flex flex-row-reverse w-1/4 h-[50px] mt-2'>
							<SortSelector
								values={exploreOrders}
								onSelect={(o) => setSelectedExploreOrder(o)}
							/>
						</div>
					</div>
					<GenericPreviewList<StreamInfo>
						items={exploreStreams}
						itemsProvider={async (f: number, t: number) =>
							itemsProvider(f, t,
								exploreStreams,
								setExploreStreams,
								setHasMoreExpoloreStreams,
								selectedCategory ?
									(f, c, o) => fetchCategoryStreams(f, c, selectedCategory.name, o) :
									(f, c, o) => fetchRecommendedStreams(f, c, o),
								selectedExploreOrder)
						}
						hasMoreData={hasMoreExploreStreams}
						renderItem={streamRenderer}
						renderLoading={loadingStreamRenderer}
						relativeHeight={75}
					/>
				</div>
			</div>
		</div>

	)

}


