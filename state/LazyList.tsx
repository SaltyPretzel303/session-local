import React, { createRef, Fragment, PureComponent, useRef } from "react";
import { FixedSizeList, FixedSizeList as List } from "react-window";
import InfiniteLoader from "react-window-infinite-loader";
import AutoSizer, { VerticalSize } from "react-virtualized-auto-sizer"

const LOADING = 1;
const LOADED = 2;
let itemsStatus: boolean[] = [];

const isItemLoaded = (index: number) => index < itemsStatus.length && itemsStatus[index];
const loadMoreItems = (startIndex: number, stopIndex: number): Promise<void> => {
	console.log("Loading items from: " + startIndex + "-" + stopIndex)
	for (let index = startIndex; index <= stopIndex; index++) {
		if (index >= itemsStatus.length) {
			itemsStatus.push(false)
		} else {
			itemsStatus[index] = false
		}
	}

	return new Promise(resolve =>
		setTimeout(() => {
			for (let index = startIndex; index <= stopIndex; index++) {
				itemsStatus[index] = true;
			}
			resolve();
		}, 100)
	);
};

function Row({ index, style }: { index: number, style: any }) {
	if (itemsStatus[index]) {
		return (
			<div style={style} className='flex flex-row box-border'>
				<p>item</p>
				<p>{index}</p>
			</div>
		)
	} else {
		return <div style={style} className='border border-cyan-400'>Loading ... </div>
	}
}

export function LazyList() {

	const listRef = useRef<FixedSizeList<any> | null>()
	let current = 0
	const step = 4

	function moreClick() {
		let next = current + step
		listRef.current?.scrollToItem(next)
		current = next
	}

	function lessClick() {
		let next = current - step
		if (next < 0) {
			next = 0
		}

		listRef.current?.scrollToItem(next)
		current = next
	}

	return (
		<div className='flex flex-row h-full w-2/3 border-2 border-black'>
			<InfiniteLoader
				isItemLoaded={isItemLoaded}
				itemCount={100}
				loadMoreItems={loadMoreItems}>
				{
					({ onItemsRendered, ref }) => (
						<AutoSizer disableWidth>
							{
								({ height }: { height: number }) => {
									return (
										<List
											className="border-4 border-black m-2"
											direction="vertical"

											height={height}
											width={300}

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
									)
								}
							}
						</AutoSizer>
					)

				}
			</InfiniteLoader>

			<div className='flex w-1/2 h-[300px] border-2 border-red-500'></div>
		</div>
	);
}

function SimpleRow({ index, style }: { index: number, style: any }) {
	return (
		<div style={style} className='border border-black'>
			<p className='text-xl'>ELEMENT: {index}</p>
		</div>
	)
}

export default function SimpleList() {
	return (
		<div className='min-h-[500px] min-w-[400px] border-2 border-red-600 h-screen flex justify-center items-center'>

			<div className=' 
					pt-2 pl-2 
					h-1/2 w-1/2 
					border-4 border-purple-500'>
				<AutoSizer>
					{({ height, width }: { height: number, width: number }) => (
						<InfiniteLoader
							isItemLoaded={isItemLoaded}
							itemCount={200}
							loadMoreItems={loadMoreItems}
						>
							{({ onItemsRendered, ref }) => {
								return (
									<List
										className="border-2 border-yellow-500"
										height={height - 20}
										width={width - 20}
										itemCount={200}
										itemSize={40}
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

		</div>
	)
}

export function Columns() {
	return (
		<div className='flex flex-row w-full h-full border-2 border-black p-10 min-w-[400px]'>
			<div className='border border-blue-500 ml-5 w-[300px]'>
				one
			</div>
			<div className='border border-red-500 ml-5 w-[300px] max-[700px]:hidden'>
				two
			</div>
			<div className='border border-green-500 ml-5 w-[300px] max-[1000px]:hidden'>
				three
			</div>
		</div>
	)
}
