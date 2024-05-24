import React, { useEffect } from "react"
import useWebSocket from "react-use-websocket"
import { ChatMessage, ChatMsgType, UserInfo } from "../Datas"
import { WebSocketMessage } from "react-use-websocket/dist/lib/types"
import config from "../Config"
import GenericPreviewsList from "./GenericPreviewList"

export default function Chat({ channel, getUser }:
	{
		channel: string,
		getUser: () => Promise<UserInfo | undefined>
	}) {

	const [messages, setMessages] = React.useState<ChatMessage[]>([])
	const [myMessage, setMyMessage] = React.useState<string>("")
	const { sendJsonMessage, lastJsonMessage: newJsonMessage, readyState } =
		useWebSocket<ChatMessage>(config.chatRelayUrl(channel));

	useEffect(() => {
		if (newJsonMessage) {
			console.log("Received message: " + JSON.stringify(newJsonMessage))
			setMessages([newJsonMessage, ...messages])
		}
	}, [newJsonMessage])

	async function sendMessage() {
		console.log("Sending message: " + myMessage)

		let user = await getUser()
		if (!user) {
			console.log("User not found, sending not allowed.")
			return
		}

		let message = {
			sender: user.username,
			type: ChatMsgType.text,
			txtContent: myMessage
		} as ChatMessage

		sendJsonMessage(message)

		setMyMessage("")
		console.log("Message sent: " + JSON.stringify(message))
	}

	async function keyPressHandler(e: React.KeyboardEvent) {
		if (e.key == 'Enter') {
			sendMessage()
		}
	}

	function Message({ ind, message }: { ind: number, message: ChatMessage }) {
		let light = "bg-gray-100 text-black"
		let dark = "bg-gray-400 text-white"
		let bg = ind % 2 == 0 ? light : dark
		let content = `${message.sender}: ${message.txtContent}`

		return (
			<div className={`flex w-full
				px-2 text-base
				rounded-xl
				${bg} mb-2`}
				key={ind}>
				{content}
			</div>
		)
	}

	return (
		<div className='flex flex-col size-full 
				justify-center items-center
				pr-2'>

			<div className='flex flex-row w-[80%]
				justify-center items-center
				mb-2 p-2
				border-b border-b-slate-800
				'>
				<p>Chat</p>
			</div>
			<div className='flex flex-col-reverse 
					size-full 
					items-center
					overflow-scroll'>

				{messages.map((m, ind) => <Message key={ind} ind={ind} message={m} />)}
			</div>

			<div className='flex h-[1px] w-full border-t border-t-slate-800 my-2'></div>
			<input className='flex w-full h-[30px] 
				text-black rounded-xl
				px-2'
				placeholder="Type message"
				value={myMessage}
				onKeyUp={keyPressHandler}
				onChange={(e) => setMyMessage(e.target.value)} />

			<button className='w-full 
				my-3 p-1 
				rounded-xl
				border
				hover:border hover:border-orange-500'
				onClick={(e) => sendMessage()}>Send</button>
		</div >

	)
}