import InfiniteLoader from 'react-window-infinite-loader'
import { FixedSizeList as List } from 'react-window'
import { useRef } from 'react'
import { StreamInfo, StreamsOrdering } from '../Datas'

type PropsType = {
	title: string,
	streamsProvider: (from: number,
		to: number,
		ordering: StreamsOrdering) => Promise<StreamInfo[]>

	streamClickHandler: (stream: StreamInfo) => void
}

type range = {
	start: number,
	count: number
}

export default function VertPreviewList(props: PropsType) {

	const listRef = useRef<List<any> | null>()

	const cacheSize = 10
	const cacheTreshold = 2

	let DATA: { [index: number]: StreamInfo | undefined } = {}

	function addData(index: number, newData: StreamInfo) {
		DATA[index] = newData

		let cachedKeys: number[] = Object.keys(DATA).map(s => parseInt(s))
		let cachedLen = cachedKeys.length

		if (cachedLen > cacheSize + cacheTreshold) {
			let sorted = cachedKeys.sort()

			if (index < sorted[0]) {
				removeFromTheTop(sorted, cacheTreshold)
			} else {
				removeFromTheBottom(sorted, cacheTreshold)
			}

		}

	}

	function removeFromTheTop(keys: number[], count: number) {
		console.log("Clearing form the top: " + count)

		let len = keys.length
		for (let i = len - 1; i >= len - count; i--) {
			if (i < 0) {
				return
			}

			delete DATA[keys[i]]
			console.log("Cleared: " + keys[i])
		}
	}

	function removeFromTheBottom(keys: number[], count: number) {
		console.log("Clearing form the bottom: " + count)

		let len = keys.length
		for (let i = 0; i < count; i++) {
			if (i >= len) {
				return
			}

			delete DATA[keys[i]]
			console.log("Cleared: " + keys[i])
		}

	}

	function isItemLoaded(index: number): boolean {
		return (index in DATA && DATA[index] != undefined)
	}

	async function loadMoreItems(fromInd: number, toInd: number): Promise<void> {
		console.log("Loading: " + fromInd + "-" + toInd)
		for (let i = fromInd; i < toInd; i++) {
			DATA[i] = undefined
		}

		let newData = await props.streamsProvider(fromInd, toInd, StreamsOrdering.None)

		let newLen = newData.length
		console.log("Received new data: " + newLen)
		for (let key in DATA) {
			console.log(key)
		}

		for (let i = fromInd; i < fromInd + newLen; i++) {
			DATA[i] = newData[i]
		}

		if (newLen < toInd - fromInd) {
			for (let i = fromInd + newLen; i < toInd; i++) {
				delete DATA[i]
			}
		}

		return
	}

	function StreamPreview({ index, style }: { index: number, style: any }) {
		let singleData: StreamInfo | undefined = DATA[index]

		if (singleData) {

			return (
				<div style={style}>
					<div className='flex flex-row border border-yellow-300 p-2 m-2'>
						<h1 className='border-1 border-gray-300'>{singleData.title}</h1>
						<h1>{singleData.creator}</h1>
					</div>

				</div>
			)
		} else {
			return (
				<div className='border-1 border-orange-300'>
					<h1>LOADING ...</h1>
				</div>
			)

		}
	}

	return (
		<div className='flex flex-col w-[320px] h-full
					border-2 border-black'>
			<InfiniteLoader
				isItemLoaded={isItemLoaded}
				loadMoreItems={loadMoreItems}
				itemCount={200}
			>

				{({ onItemsRendered, ref }) => {
					return <List
						className='border border-white h-full'
						height={300}
						width={300}
						itemCount={200}
						itemSize={100}
						onItemsRendered={onItemsRendered}
						ref={(lRef) => {
							ref(lRef)
							listRef.current = lRef
						}}
					>
						{StreamPreview}
					</List>
				}}

			</InfiniteLoader>
		</div>
	)
}

{/* <div className='flex flex-col border-2 border-green-500 w-1/2'>
<button className='h-full w-[30px]' onClick={lessClick}>-</button>
<InfiniteLoader
	// ref={listRef}
	isItemLoaded={isItemLoaded}
	itemCount={100}
	loadMoreItems={loadMoreItems}
>
	{({ onItemsRendered, ref }) => (
		<List

			direction="vertical"
			className="border border-black"
			height={400}
			width={100}

			itemCount={1000}
			itemSize={100}

			onItemsRendered={onItemsRendered}
			ref={(l) => {
				ref(l)
				listRef.current = l
			}}
		>
			{Row}
		</List>
	)}

</InfiniteLoader>
<button className='h-full w-[30px]' onClick={moreClick}>+</button>
</div> */}
