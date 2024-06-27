import React from "react";
import { useNavigate } from "react-router-dom"
import GenericLazyList from "./GenericLazyList";
import config from "../Config";
import { StreamInfo, UserInfo } from "../Datas";

export default function Search({ getUser }: { getUser: () => Promise<UserInfo | undefined> }) {

	const [items, setItems] = React.useState<StreamInfo[]>([])
	const [hasMoreItems, setHasMoreItems] = React.useState<boolean>(false)

	const [query, setQuery] = React.useState<string>('')

	const [sTimeout, setSTimeout] = React.useState<NodeJS.Timeout>()
	const navigate = useNavigate()

	async function itemsProvider(f: number, t: number): Promise<void> {
		console.log(`Query fetching: ${f}-${t} for: ${query}`)

		if (!query) {
			console.log("Query not provided.")
			setItems([])
			setHasMoreItems(false)
			return
		}

		let url = config.streamSearchUrl(query, f, t - f, config.myRegion)
		try {
			let res = await fetch(url)
			if (res.status != 200) {
				throw Error("Stream query fetch status: " + res.status)
			}

			let newItems: StreamInfo[] = await res.json()
			console.log("Received count: " + newItems.length)

			setItems([...items, ...newItems])

			if (newItems.length < t - f) {
				setHasMoreItems(false)
			}

		} catch (e) {
			console.log("Error while fetching stream query: " + e)
			setHasMoreItems(false)
			return
		}

	}

	function RenderSearchItem(item: StreamInfo) {
		return (
			<div className='flex flex-col 
					w-full h-[50px] 
					px-2
					border-2 bg-gray-400
					rounded-2xl
					justify-start items-center'>

				<div className='flex flex-row w-full h-full items-center'
					onClick={() => ResultClick(item)}>
					{item.creator} - {item.title || "Not live"}
				</div>

			</div>
		)
	}

	function RenderLoadingSearchItem() {
		return (<div className='flex w-full h-[50px] border-2 border-black'></div>)
	}


	async function ResultClick(item: StreamInfo) {
		console.log("Clicked on: " + JSON.stringify(item))

		let user = await getUser()
		if (!user) {
			console.log("Authenticate to open player page.")
			return
		}

		navigate("/watch/" + item.creator)
	}

	function onType(e: React.ChangeEvent<HTMLInputElement>) {
		setQuery(e.target.value)

		clearTimeout(sTimeout)
		setSTimeout(setTimeout(() => {
			setHasMoreItems(query != "")
			setItems([])
		}, 400))
	}

	return (
		<div className='flex flex-col 
			w-full 
			absolute top-[5px]
			justify-start items-start'>

			<input className='flex w-full h-[40px] rounded-2xl px-2'
				placeholder="Search live streams "
				onChange={onType}
				onBlur={() => setItems([])} />

			{(hasMoreItems || items.length > 0) &&
				<div className='flex w-full h-[250px]
						py-2 
						bg-slate-900 rounded-2xl
						border border-slate-700'>

					<GenericLazyList<StreamInfo>
						items={items}
						hasMoreData={hasMoreItems}
						itemsProvider={itemsProvider}
						relativeHeight={20}
						renderItem={RenderSearchItem}
						renderLoading={RenderLoadingSearchItem}
					/>
				</div>}
		</div>
	)
}