import { useEffect, useState } from "react"
import StreamPreview from "./StreamPreview"
import { StreamInfo, StreamsOrdering } from "../Datas"
import AutoSizer from "react-virtualized-auto-sizer"
import { FixedSizeList as List } from 'react-window'
import InfiniteLoader from "react-window-infinite-loader"

type PreviewListProps = {
	title: string,
	streamsProvider: (from: number,
		to: number,
		ordering: StreamsOrdering) => Promise<StreamInfo[]>
	streamClickHandler: (stream: StreamInfo) => void
}

export default function PreviewsList(props: PreviewListProps) {

	const visibleCount = 4

	let streams: { [index: number]: (StreamInfo | undefined) } = {}

	function isItemLoaded(index: number): boolean {
		return (index in streams && streams[index] != undefined)
	}

	async function loadMoreItems(start: number, end: number): Promise<void> {
		console.log("Loading " + start + "-" + end)
		for (let i = start; i < end; i++) {
			if (!(i in streams)) {
				streams[i] = undefined
			}
		}

		clearOld()

		let newStreams = await props.streamsProvider(start, end, StreamsOrdering.None)

		for (let i = start; i < end; i++) {
			let stream = newStreams.shift()
			if (!stream) {
				delete streams[i]
			} else {
				streams[i] = stream
			}

		}

	}

	function Row({ index, style }: { index: number, style: any }) {

		let info: StreamInfo | undefined = streams[index]

		if (info != undefined) {


			if (info === undefined) {
				console.log("INFO IS UNDEFINED")
			}

			// return <StreamPreview info={info}
			// 	onClick={props.streamClickHandler}
			// 	style={style} />
			return (

				<div className='border-2 border-purple-400 w-[full] h-[full] align-center' style={style}>
					{info.title}
				</div>
			)
		} else {
			return (
				<div className='border-2 border-black w-[full] h-[full] align-center' style={style}>
					LOADING ....
				</div>
			)
		}
	}


	function clearOld() {

	}

	return (
		<div className='min-h-[500px] min-w-[400px] 
				h-full w-full
				flex justify-center items-center
				p-5
				bg-blue-900'>

			<div className='w-full h-full'>

				<AutoSizer>
					{({ height, width }: { height: number, width: number }) => (
						<InfiniteLoader
							isItemLoaded={isItemLoaded}
							itemCount={2000}
							loadMoreItems={loadMoreItems}
						>
							{({ onItemsRendered, ref }) => {
								return (
									<List
										className="border"
										height={height}
										width={width}
										itemCount={200}
										itemSize={120}
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