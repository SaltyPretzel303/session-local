import Overlay from 'react-modal'
import { useEffect, useState } from 'react'
import {
	UserInfo,
	KeyResponse,
	isKeySuccess,
	failure as keyFailure,
	StreamInfo,
	UpdateRequest
} from '../Datas'

import config from '../Config'
import { json } from 'stream/consumers'

type userInfoProps = {
	isVisible: boolean
	setVisible: React.Dispatch<boolean>
	logoutHandler: () => void
	getUser: () => Promise<UserInfo | undefined>
}

export default function UserInfoPopup(props: userInfoProps) {

	const [userInfo, setUserInfo] = useState<UserInfo | undefined>(undefined)
	const [streamKeyError, setStreamKeyError] = useState<string | undefined>(undefined)
	const [isLoadingKey, setIsLoadingKey] = useState<boolean>(false)
	const [streamKey, setStreamKey] = useState<KeyResponse | undefined>(undefined)

	const [streamInfo, setStreamInfo] = useState<StreamInfo | undefined>()
	const [category, setCategory] = useState<string>("chatting")

	const [title, setTitle] = useState<string>("Stream title")
	const [categories, setCategories] = useState<string[]>([])
	const [isRefreshing, setIsRefreshing] = useState<boolean>(false)
	const [updateStatus, setUpdateStatus] = useState<"updating" | "success" | "failed">()

	useEffect(() => {
		if (!props.isVisible) {
			return
		}

		if (props.isVisible && streamKey && isExpired(streamKey.exp_date)) {
			console.log("Key expired, clearing previous data.")
			setStreamKey(undefined)
			setStreamKeyError("Url expired, request new.")
		}

		console.log("Will fetch user data.")

		fetchData()

	}, [props.isVisible])

	async function fetchData() {
		let user = await props.getUser()

		if (!user) {
			// can't be undefined
			return
		}

		setUserInfo(user)

		setStreamInfo(await loadStreamInfo(user?.username))

		setCategories(await loadCategories())
	}

	async function loadStreamInfo(username: string): Promise<StreamInfo | undefined> {

		try {
			let res = await fetch(config.streamInfoUrl(username, config.myRegion))

			if (res.status != 200) {
				throw Error("status code: " + res.status)
			}

			let data = await res.json() as StreamInfo

			console.log("Stream info: ")
			console.log(JSON.stringify(data))

			return data
		} catch (e) {
			console.log("Failed to load stream info: " + e)
			return undefined
		}

	}

	function isExpired(expDate: string) {
		return (new Date(expDate)) < new Date()
	}

	async function revealStreamKeyClick() {
		setIsLoadingKey(true)
		let keyResponse = await fetchKey(config.streamKeyUrl)

		if (!isKeySuccess(keyResponse.status)) {
			setStreamKeyError(keyResponse.message)

			setIsLoadingKey(false)
			setStreamKey(undefined)
			setStreamKeyError(keyResponse.message)

			return
		}

		setStreamKey(keyResponse)
		setIsLoadingKey(false)
		setStreamKeyError(undefined)
	}

	async function fetchKey(keyUrl: string): Promise<KeyResponse> {
		console.log("Will request stream key.")
		return fetch(keyUrl)
			.then(async (res) => {
				if (res.status != 200) {
					console.log("Got non 200 code for stream key.")
					keyFailure("Failed to obtain stream key")
				}

				// console.log("Response: ")
				// console.log(await res.text())

				return (await res.json()) as KeyResponse
			})
			.catch((err) => {
				console.log("Error while fetching stream key: " + err)
				return keyFailure("Failed to obtain stream key.")
			})
	}

	function logoutClick() {
		props.setVisible(false)
		props.logoutHandler()
	}

	function StreamKey() {
		if (isLoadingKey) {
			return (
				<img
					className='m-0 p-0 w-1/12 h-1/3'
					src={"loading.gif"} />
			)
		} else {
			if (streamKey) {
				return (
					<p className='text-xl 
						border-2 border-purple-500 
						w-full 
						p-2 box-border'>
						http://session.com/ingest/{streamKey.value}
					</p>
				)
			} else {
				return (
					<button
						className='w-3/4 h-full 
						border border-purple-400
						bg-purple-500 rounded-md
						font-bold'
						onClick={revealStreamKeyClick}
					>Click to generate url</button>
				)
			}
		}
	}

	function formatDate(strDate: string): string {
		return (new Date(strDate)).toLocaleString("de-CH")
	}

	async function loadCategories(): Promise<string[]> {
		try {
			let res = await fetch(config.categoriesUrl)

			if (res.status != 200) {
				throw Error("status code: " + res.status)
			}

			return await res.json() as string[]

		} catch (e) {
			console.log("Failed to load categories: " + e)
			return []
		}
	}

	function LiveIndicator() {
		if (streamInfo) {
			return (
				<div className='flex flex-row'>
					<div className='w-[20px] h-[20px]
						border-2 border-red-600
						bg-red-600
						rounded-full mx-2'></div>
					<p className='text-red-500'>You are live!</p>
				</div>
			)
		} else {
			return (
				<div className='flex flex-row'>
					<div className='w-[20px] h-[20px]
						border-2 border-black 
						rounded-full mx-2'></div>
					<p className='text-s'>Stream offline</p>
				</div>
			)
		}
	}

	async function refresh() {
		setIsRefreshing(true)
		let username = userInfo?.username
		if (!username) {
			// can't be undefined btw
			return
		}

		setStreamInfo(await loadStreamInfo(username))

		setIsRefreshing(false)
	}

	async function updateStream() {
		if (!streamInfo || !userInfo) {
			// has to be !undefined but still ... 
			return
		}

		setUpdateStatus("updating")
		console.log("Updating: " + userInfo.username)
		console.log("Updating with: " + title)
		console.log("Updating with: " + category)

		let updateData = {
			username: userInfo.username,
			title: title,
			category: category,
			is_public: true
		} as UpdateRequest

		let reqOptions = {
			method: "POST",
			body: JSON.stringify(updateData),
			headers: [['Content-type', 'application/json']]
		} as RequestInit

		try {
			let res = await fetch(config.updateStreamUrl, reqOptions)
			if (res.status != 200) {
				throw Error("Status code: " + res.status)
			}

			setUpdateStatus("success")

		} catch (e) {
			console.log("Failed to update stream info: " + e)
			setUpdateStatus("failed")
		}



	}

	function renderUpdateStaus() {
		switch (updateStatus) {
			case 'updating':
				return (
					<p className='text-purple-400'>Processing stream update.</p>
				)
			case 'failed':
				return (
					<p className='text-red-600'>Failed to update stream</p>
				)
			case 'success':
				return (
					<p className='text-green-500'>Stream updated.</p>
				)
		}
	}

	return (
		<Overlay

			className="flex w-full h-full
					items-center justify-center text-center
					text-gray-300"

			ariaHideApp={false}
			isOpen={props.isVisible}
			shouldCloseOnEsc={true}
			onRequestClose={() => props.setVisible(false)}>

			<div
				className="flex flex-col 
					min-w-[200px] max-w-[480px]
					min-h-[450px]
					items-center align-middle
					bg-sky-900
					p-9 
					border-2 border-purple-700 rounded-3xl">

				<h1 className="mb-2 font-bold text-purple-400 text-2xl ">
					{userInfo ? userInfo.username : "USERNAME"}
				</h1>

				<div className='flex flex-row items-center'>
					<h2 className='mr-2'>Email: </h2>
					<h2 className='text-xl'>{userInfo?.email}</h2>
				</div>


				<hr className='w-3/4 my-4'></hr>

				<h1 className="font-bold text-purple-400 text-2xl">Start Streaming</h1>
				<p className='my-4 text-center'>
					In order to stream copy this generated url and paste it in
					you streaming client (obs or similar software).
				</p>

				{/* Error message  */}
				{streamKeyError && <p className='text-red-400'>{streamKeyError}</p>}

				{/* Ingest url container */}
				<div
					className='p-0 m-0 
					border-b-orange-500
					w-full h-10'>

					<StreamKey />

				</div>

				{/* Expiration date and DoNotShare message */}
				{streamKey &&
					<div className='flex flex-col mt-3'>
						<p>This is unique single use url.</p>
						<p>Will expire at: {formatDate(streamKey?.exp_date)}</p>
						<p className='font-bold text-lg text-red-400'>Do not share this URL !!!</p>
					</div>
				}

				<hr className="w-3/4 my-4 mb-6"></hr>

				<LiveIndicator />

				{/* Update stream form */}
				<div className='flex flex-col 
					w-5/6 mt-2
					border-2 border-purple-500 rounded-2xl
					p-4 pb-1
					text-left'>

					<label className='ml-1'>Title</label>
					<input className='rounded-md mb-2 text-black p-1'
						defaultValue={streamInfo?.title}
						// value={title}
						onChange={e => setTitle(e.target.value)}
					/>

					<label className='ml-1'>Category</label>
					<select className="rounded-lg text-xl p-1 text-black w-3/4"
						defaultValue={streamInfo?.category}
						// value={category}
						onChange={(e) => setCategory(e.target.value)}
					>

						{categories.map((c) => <option key={c} value={c}>{c}</option>)}

					</select>

					<div className="flex flex-rowjustify-center items-center my-4 mb-0" >

						<div className='flex w-1/2 justify-center'>

							<button className='w-[50px] h-[50px] 
								rounded-full 
								disabled:bg-gray-300
								enabled:hover:border-2 enabled:hover:border-purple-500'
								disabled={isRefreshing}
								onClick={refresh}>
								<img src='refresh.png' />
							</button>

						</div>

						<div className='flex flex-row-reverse
									w-1/2 p-4'>

							<button className='bg-purple-500 rounded-lg 
							text-xl px-4 py-1
							box-border
							border-2 border-transparent
							enabled:hover:border-2 enabled:hover:border-purple-400
							disabled:bg-slate-400'
								disabled={!streamInfo}
								onClick={updateStream}>
								Update</button>
						</div>

					</div>
					<div className="m-0 min-h-[20px] flex justify-center">
						{renderUpdateStaus()}
					</div>
				</div>
				{/* Update stream form done */}

				<div className='flex flex-row justify-end align-middle
							w-full mt-6'>

					<button
						className='bg-red-500 rounded-2xl 
							text-white text-xl 
							border-2 border-transparent
							hover:border-2 hover:border-purple-400 box-border
							px-4 py-2 mt-6'
						onClick={logoutClick}>Logout</button>
				</div>


			</div>


		</Overlay>
	)
}
