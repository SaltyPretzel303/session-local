import "./style/ExplorePage.css"
import User from "./data_model/User";
import { PreviewsContainer } from "./components/PreviewsContainer";
import { useEffect, useState } from "react";
import { StreamInfo } from "./data_model/StreamInfo";

export interface ExploreProps {
	user: User | null
}
export function Explore(props: ExploreProps) {

	const [followed, setFollowed] = useState<StreamInfo[]>([])
	const [toExplore, setToExplore] = useState<StreamInfo[]>([])

	useEffect(() => {

		// if (props.user === null) {
		// 	return
		// }

		populateFollowed([])
		populateExplore()
	}, [])

	async function populateFollowed(followed_names: string[]) {
		console.log("Populating followed ")

		let streams_res = await fetch("http://localhost:8002/get_followed/some_stream")
		if (streams_res.status != 200) {
			console.log("Failed to obtain followed streams ...")
			return
		}

		console.log("Successfully obtained followed streams info ...")

		let data = await streams_res.json()
		if (data === null) {
			console.log("Failed to parse data to json ... ")
			return
		}

		setFollowed([...followed, ...data])
	}

	async function populateExplore() {
		console.log("Populating to explore ...")

		let explore_res = await fetch("http://localhost:8002/get_explore")
		if (explore_res.status != 200) {
			console.log("Failed to obtain explore streams ... ")
			return
		}

		console.log("Successfully obtained to explore streams ... ")

		let data = await explore_res.json()
		if (data === null) {
			console.log("Received invalid data as explore streams  ... ")
			return
		}

		setToExplore([...toExplore, ...data])
	}

	// function genStreamInfo(n: number): StreamInfo {
	// 	return {
	// 		title: `title_${n}`,
	// 		creator: `creator_${n}`,
	// 		category: "chatting",
	// 		viewers: n
	// 	} as StreamInfo
	// }

	return (
		<div className="explorePage">
			{followed.length > 0 ? <PreviewsContainer title={"Following"} streams={followed} /> : null}
			<PreviewsContainer title={"Explore"} streams={toExplore} />
		</div>
	);
}
