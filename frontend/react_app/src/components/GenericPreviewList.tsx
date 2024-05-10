import React from "react"
import AutoSizer from "react-virtualized-auto-sizer"
import { FixedSizeList as List } from 'react-window'
import InfiniteLoader from "react-window-infinite-loader"

export default function GenericPreviewsList<T>(
	{
		dataProvider,
		renderItem,
		itemSize: size
	}: {
		dataProvider: (from: number, to: number) => Promise<T[]>
		renderItem: (item: T) => JSX.Element
		itemSize: number
	}
) {

	const [hasMoreData, setHasMoreData] = React.useState<boolean>(true)

	const [data, setData] = React.useState<T[]>([])

	let itemsCount = hasMoreData ? data.length + 1 : data.length

	function isItemLoaded(index: number): boolean {
		return !hasMoreData || index < data.length
	}

	async function loadMoreItems(start: number, end: number): Promise<void> {
		console.log(`Requesting: ${start} - ${end} = ${end - start}`)

		let newData = await dataProvider(start, end)

		console.log(`Received: ${newData} = ${newData.length}`)

		if (newData.length > 0) {
			setData([...data].concat(newData))
		}

		if (newData.length < end - start) {
			setHasMoreData(false)
		}
	}

	function Row({ index, style }: { index: number, style: any }) {
		if (isItemLoaded(index)) {
			let info: T = data[index]
			return (
				<div className='flex 
					w-full h-full
					border-[20px] box-border border-sky-900
					justify-center items-center'
					style={style}>

					{renderItem(info)}

				</div>
			)
		} else {
			return (
				<div className='flex border-2 border-black 
					w-full h-full 
					justify-center items-center
					p-4
					bg-slate-300'
					style={style}>

					<p>Loading ... </p>

				</div>
			)
		}

	}


	return (
		<div className='flex flex-col h-full w-full'>

			<AutoSizer>
				{({ height, width }: { height: number, width: number }) => (
					<InfiniteLoader
						isItemLoaded={isItemLoaded}
						itemCount={2000}
						loadMoreItems={loadMoreItems}
						threshold={5}
					>
						{({ onItemsRendered, ref }) => {
							return (
								<List
									height={height}
									width={width}
									itemCount={itemsCount}
									itemSize={size}
									onItemsRendered={onItemsRendered}
									ref={ref}
								>
									{Row}
								</List>
							)
						}}

					</InfiniteLoader>
				)}
			</AutoSizer>
		</div>
	)
}