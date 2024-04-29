import { useEffect, useState } from "react"
import StreamPreview from "./StreamPreview"
import { StreamInfo, StreamsOrdering } from "../Datas"

type PreviewListProps = {
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


export default function PreviewsList(props: PreviewListProps) {

	const visibleCount = 4

	const [streams, setStreams] = useState<StreamInfo[]>([])
	const [currentRange, setCurrentRange] = useState<range>({ start: 0, count: 0 })

	useEffect(() => {
		async function fetchData() {
			let newStreams = await props.streamsProvider(0,
				visibleCount,
				StreamsOrdering.Views)

			if (newStreams.length > 0) {
				console.log(`Populating ${props.title} list with ${newStreams.length} streams.`)
			}


			setStreams(newStreams)
			setCurrentRange({ start: 0, count: newStreams.length })
		}

		fetchData()

	}, [])

	type scrollProps = {
		dir: "left" | "right"
		clickHandler: () => void
	}

	function ScrollButton(props: scrollProps) {

		return (
			<button
				className='border border-black 
					w-14 h-28 
					rounded-full mx-4
					text-xl font-bold'
				onClick={props.clickHandler}>

				{props.dir === "left" ? "<" : ">"}
			</button>
		)
	}

	async function scrollNext() {
		if (currentRange.count < visibleCount) {
			// Last provider call returned the last streams. (no more streams)
			// Or maybe ask once more ... maybe someone started a stream ...
			return
		}

		let newFrom = currentRange.start + currentRange.count
		let newStreams = await props.streamsProvider(newFrom,
			visibleCount,
			StreamsOrdering.Views)

		if (newStreams.length == 0) {
			console.log(`0 new streams fetched from: ${newFrom}.`)
			return
		}

		setStreams(newStreams)
		setCurrentRange({ start: newFrom, count: newStreams.length })
	}

	async function scrollBack() {
		if (currentRange.start == 0) {
			console.log("We are at the begining.")
			return
		}

		let newFrom = currentRange.start - visibleCount
		newFrom = newFrom >= 0 ? newFrom : 0

		let oldStreams = await props.streamsProvider(newFrom,
			visibleCount,
			StreamsOrdering.Views)

		if (oldStreams.length == 0) {
			console.log(`0 old streams fetched from: ${newFrom}.`)
			return
		}

		// TODO once again I am asking for some animation. 
		setStreams(oldStreams)
		setCurrentRange({ start: newFrom, count: oldStreams.length })
	}

	return (
		<div className='flex flex-col 
			border-y-4 border-purple-500
			p-2 my-3 h-60'>

			<h1 className='h-10 ml-[160px] 
				font-bold
				text-purple-500 text-2xl'>{props.title}</h1>

			<div className='flex flex-row
				items-center justify-center
				h-full box-border'>

				{<ScrollButton dir={"left"} clickHandler={scrollBack} />}

				{/* streams container */}
				<div className='flex flex-row
						h-full basis-10/12 
						justify-center
						box-border p-2
						border-2 border-blue-900
						'>

					{
						streams.map((stream) =>
							<StreamPreview
								key={stream.creator}
								info={stream}
								onClick={props.streamClickHandler} />)
					}

				</div>

				{<ScrollButton dir={"right"} clickHandler={scrollNext} />}

			</div>


		</div>
	)
}