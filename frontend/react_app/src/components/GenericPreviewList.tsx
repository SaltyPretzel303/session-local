import AutoSizer from "react-virtualized-auto-sizer"
import { InfiniteLoader, List, ListRowProps } from 'react-virtualized'
import React from "react"

export default function GenericPreviewsList<T>(
	{
		items,
		itemsProvider,
		hasMoreData,
		renderItem,
		renderLoading,
		relativeHeight,
	}: {
		items: T[],
		itemsProvider: (from: number, to: number) => Promise<void>
		hasMoreData: boolean
		renderItem: (item: T) => JSX.Element
		renderLoading: () => JSX.Element
		relativeHeight: number
	}
) {

	const loaderRef = React.useRef<InfiniteLoader>(null)
	let itemsCount = hasMoreData ? items.length + 1 : items.length
	let heightRatio = relativeHeight < 0 ? 0 : relativeHeight > 100 ? 100 : relativeHeight

	React.useEffect(() => {
		if (hasMoreData) {
			console.log("Reloading list. ")
			loaderRef.current?.resetLoadMoreRowsCache(true)
		}
	}, [hasMoreData])

	function isItemLoaded(index: number): boolean {
		return !hasMoreData || index < items.length
	}

	function Row({ index, style }: { index: number, style: any }) {
		let content = undefined
		if (isItemLoaded(index)) {
			let info: T = items[index]
			content = renderItem(info)
		} else {
			content = renderLoading()
		}

		return (
			<div className='flex size-full justify-center items-center'
				key={index}
				style={style}>

				<div className='flex size-full box-border px-2 py-3'>
					{content}
				</div>

			</div>
		)
	}

	async function loadMoreRows(prop: { startIndex: number, stopIndex: number }): Promise<void> {
		itemsProvider(prop.startIndex, prop.stopIndex)
	}

	return (
		<div className='flex flex-col size-full'>

			<AutoSizer>
				{({ height, width }: { height: number, width: number }) => (
					<InfiniteLoader
						ref={loaderRef}
						isRowLoaded={(prop: { index: number }) => isItemLoaded(prop.index)}
						rowCount={1000}
						loadMoreRows={loadMoreRows}
					>
						{({ onRowsRendered, registerChild }) => {
							return (
								<List
									ref={registerChild}
									onRowsRendered={onRowsRendered}
									height={height}
									width={width}
									rowCount={itemsCount}
									rowHeight={width * heightRatio / 100}
									rowRenderer={(props: ListRowProps) => Row(props)}
								/>

							)
						}}

					</InfiniteLoader>
				)}
			</AutoSizer>
		</div>
	)
}