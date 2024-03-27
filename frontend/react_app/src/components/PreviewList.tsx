import { useEffect, useState } from "react"
import StreamPreview from "./StreamPreview"
import { StreamInfo } from "../Datas"

type PreviewListProps = {
	title: string,
	streamsProvider: (from: number, to: number) => Promise<StreamInfo[]>
}

type range = {
	start: number,
	count: number
}


export default function PreviewsList(props: PreviewListProps) {

	const visibleCount = 3

	const [streams, setStreams] = useState<StreamInfo[]>([])
	const [currentRange, setCurrentRange] = useState<range>({ start: 0, count: 0 })

	useEffect(() => {
		console.log(`Constructing ${props.title} list.`)

		async function fetchData() {
			let newStreams = await props.streamsProvider(0, visibleCount)
			console.log(`Populating ${props.title} list with ${newStreams.length} streams.`)

			setStreams(newStreams)
			setCurrentRange({ start: 0, count: newStreams.length })
		}

		fetchData()

		return () => {
			console.log(`Destroying ${props.title} previews list.`)
		}

	}, [])

	type scrollProps = {
		dir: "left" | "right"
		clickHandler: () => void
	}

	function ScrollButton(props: scrollProps) {

		const focusedBorder = "2px solid green"
		const normalBorder = "0px"

		const [border, setBorder] = useState(normalBorder)

		return (
			<button
				onMouseEnter={() => setBorder(focusedBorder)}
				onMouseLeave={() => setBorder(normalBorder)}

				onClick={props.clickHandler}
				style={
					{
						border: border,
						height: "100%",
						width: "100px",
						justifyContent: "center",
						fontSize: "40px",
						marginRight: "10px",
						marginLeft: "10px"
					}
				}>
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
		let newStreams = await props.streamsProvider(newFrom, visibleCount)

		if (newStreams.length == 0) {
			console.log(`0 new streams fetched from: ${newFrom}.`)
			return
		}

		// TODO some animation would be nice 
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

		let oldStreams = await props.streamsProvider(newFrom, visibleCount)
		if (oldStreams.length == 0) {
			console.log(`0 old streams fetched from: ${newFrom}.`)
			return
		}

		// TODO once again I am asking for some animation. 
		setStreams(oldStreams)
		setCurrentRange({ start: newFrom, count: oldStreams.length })
	}

	return (
		<div style={
			{
				// width: "100%",
				height: "25vh",
				boxSizing: "border-box",
				// border: "2px dashed black",
				margin: "10px",
				padding: "10px",
				backgroundColor: "silver",
				display: "flex",
				flexDirection: "column",
				justifyContent: "flex-start"
			}
		}>
			<h1 style={
				{
					margin: 0,
					marginLeft: "30px",
					padding: 0,
					// border: "2px solid red",
					textAlign: "start",
					font: "40px Monospace"
				}
			}>{props.title}</h1>

			<div style={
				{
					display: "flex",
					flexDirection: "row"
				}
			}>
				{<ScrollButton dir={"left"} clickHandler={scrollBack} />}

				<div style={
					{
						boxSizing: "border-box",
						height: "100%",
						width: "100%",
						display: "flex",
						flexDirection: "row",
						flexWrap: "nowrap",
						overflowY: "visible", // just so that errors are visible
						overflowX: "scroll",
						border: "2px solid darkgray",
					}
				}>

					{
						streams.map((stream) =>
							<StreamPreview
								key={stream.creator}
								info={stream} />)
					}

				</div>

				{<ScrollButton dir={"right"} clickHandler={scrollNext} />}
			</div>


		</div>
	)
}