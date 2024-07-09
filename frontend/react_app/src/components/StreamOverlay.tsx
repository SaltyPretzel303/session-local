import React from 'react'
import { StreamInfo } from '../Datas'
import config from '../Config'

export default function StreamOverlay(
	{
		stream,
		chatVisible,
		setChatVisible,
		visible,
	}: {
		stream: StreamInfo | undefined,
		chatVisible: boolean,
		setChatVisible: React.Dispatch<React.SetStateAction<boolean>>,
		visible: boolean,
	}) {

	const [views, setViews] = React.useState(0)
	let intervalTimer: NodeJS.Timer | undefined = undefined
	const [isFollowing, setIsFollowing] = React.useState(false)

	React.useEffect(() => {
		if (visible) {
			loadViews()
			intervalTimer = setInterval(() => loadViews(), 5000)
		}

		checkIsFollowing()

		return () => {
			clearInterval(intervalTimer)
		}
	}, [visible])

	async function loadViews(): Promise<void> {
		if (!stream) {
			return
		}

		let url = config.viewCountUrl(stream.creator)
		let viewRes = await fetch(url)

		if (!viewRes || viewRes.status != 200) {
			console.log("Failed to fetch views count.")
			return
		}

		setViews(Number.parseInt(await viewRes.text()))
	}

	async function followClick() {
		if (!stream) {
			return
		}

		const url = config.followUrl(stream.creator)
		let res = await fetch(url)
		setIsFollowing(res.status == 200)
	}

	async function unfollowClick() {
		if (!stream) {
			return
		}

		const url = config.unfollowUrl(stream.creator)
		let res = await fetch(url)
		setIsFollowing(res.status != 200)
	}

	async function checkIsFollowing() {
		if (!stream) {
			return
		}

		let res = await fetch(config.isFollowingUrl(stream?.creator))
		setIsFollowing(res.status == 200)

	}

	function FollowButton() {
		if (isFollowing) {
			return (
				<button className='flex ml-20 w-[100px]
						px-2 justify-center
						rounded-2xl 
						text-white
						bg-slate-700 bg-opacity-40
						pointer-events-auto
						border-2 border-white
						hover:border-2 hover:border-red-600'
					onClick={unfollowClick}
				>
					Unfollow</button>
			)
		} else {
			return (
				<button className='flex ml-20 w-[100px]
						px-2 justify-center
						rounded-2xl 
						text-white
						bg-slate-700 bg-opacity-40
						pointer-events-auto
						border-2 border-white
						hover:border-2 hover:border-orange-600'
					onClick={followClick}
				>
					Follow</button>
			)
		}

	}

	return (
		<div className={`flex size-full 
			absolute
			pointer-events-none
			${visible ? 'visible' : 'hidden'}`}>


			<div className='flex flex-row 
				justify-center items-center
				w-full h-[100px] 
				px-4
				bg-gradient-to-b from-slate-900 from-50% to-transparent'>
				<div className='flex flex-col h-full w-full pt-2 pl-8'>
					<p className='text-[30px] text-white'>{stream?.title}</p>
					<div className='flex flex-row items-baseline'>
						<p className='text-[14px] text-white'>by:</p>
						<p className='text-[20px] text-white ml-2'>{stream?.creator}</p>

						<p className='text-[14px] text-white ml-20'>watching:</p>
						<p className='text-[20px] text-white ml-2'>{views}</p>
						<FollowButton />
					</div>
				</div>

				<button className='flex w-[130px] 
					border-2 rounded-xl 
					pointer-events-auto
					mb-8
					justify-center
					text-[20px]
					text-white
					bg-slate-800
					bg-opacity-45
					hover:border-2 hover:border-orange-500'
					onClick={() => setChatVisible(!chatVisible)}>
					{chatVisible ? "Hide chat" : "Show chat"}
				</button>
			</div>
		</div>
	)
}