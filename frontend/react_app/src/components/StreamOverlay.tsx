import React from 'react'
import { StreamInfo } from '../Datas'
import config from '../Config'

export default function StreamOverlay(
	{
		stream,
		chatVisible,
		setChatVisible,
		visible,
		setOverlayVisible
	}: {
		stream: StreamInfo | undefined,
		chatVisible: boolean,
		setChatVisible: React.Dispatch<React.SetStateAction<boolean>>,
		visible: boolean,
		setOverlayVisible: React.Dispatch<React.SetStateAction<boolean>>
	}) {

	const [views, setViews] = React.useState(0)
	let intervalTimer: NodeJS.Timer | undefined = undefined

	React.useEffect(() => {
		if (visible) {
			loadViews()
			intervalTimer = setInterval(() => loadViews(), 5000)
		}

		return () => {
			clearInterval(intervalTimer)
		}
	}, [visible])

	async function loadViews(): Promise<void> {
		console.log("Loading views.")
		if (!stream) {
			return
		}

		let url = config.viewCountUrl(stream.creator)
		let view_res = await fetch(url)

		if (!view_res || view_res.status != 200) {
			console.log("Failed to fetch views count.")
			return
		}

		console.log("Views loaded")
		setViews(Number.parseInt(await view_res.text()))
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
				bg-gradient-to-b from-slate-400 to-transparent'>

				<div className='flex flex-col h-full w-full pt-4'>
					<p className='text-[30px] text-black'>{stream?.title}</p>
					<div className='flex flex-row items-baseline'>
						<p className='text-[14px] text-black'>by:</p>
						<p className='text-[20px] text-black ml-2'>{stream?.creator}</p>

						<p className='text-[14px] text-black ml-20'>watching:</p>
						<p className='text-[20px] text-black ml-2'>{views}</p>
					</div>
				</div>

				<button className='flex w-[130px] 
					border rounded-xl 
					mb-6
					justify-center
					text-[20px]
					pointer-events-auto
					hover:border hover:border-orange-500'
					onClick={() => setChatVisible(!chatVisible)}>
					{chatVisible ? "Hide chat" : "Show chat"}
				</button>
			</div>
		</div>
	)
}