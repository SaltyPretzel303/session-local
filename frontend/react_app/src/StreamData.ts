// export type MediaServer = {
// 	ip: string
// 	port: number
// 	media_path: string
// 	full_path: string
// }

// export type StreamInfo = {
// 	title: string
// 	creator: string
// 	category: string
// 	viewers: number
// 	media_server: MediaServer
// }

import { StreamInfo } from './Datas'

const streams: StreamInfo[] = [
	{
		title: "Stream_1",
		creator: "user0",
		category: "chatting",
		 
		media_servers: [{
			quality: 'subsd',
			access_url: "http://localhost:10000/live/user0_subsd/index.m3u8"
		}]
	},
	{
		title: "Stream_2",
		creator: "user0",
		category: "chatting",
		 
		media_servers: [{
			quality: 'subsd',
			access_url: "http://localhost:10000/live/user0_subsd/index.m3u8"
		}]
	},
	{
		title: "Stream_3",
		creator: "user0",
		category: "chatting",
		 
		media_servers: [{
			quality: 'subsd',
			access_url: "http://localhost:10000/live/user0_subsd/index.m3u8"
		}]
	},
	{
		title: "Stream_4",
		creator: "user0",
		category: "chatting",
		 
		media_servers: [{
			quality: 'subsd',
			access_url: "http://localhost:10000/live/user0_subsd/index.m3u8"
		}]
	},
	{
		title: "Stream_5",
		creator: "user0",
		category: "chatting",
		 
		media_servers: [{
			quality: 'subsd',
			access_url: "http://localhost:10000/live/user0_subsd/index.m3u8"
		}]
	},
	{
		title: "Stream_6",
		creator: "user0",
		category: "chatting",
		 
		media_servers: [{
			quality: 'subsd',
			access_url: "http://localhost:10000/live/user0_subsd/index.m3u8"
		}]
	},
	{
		title: "Stream_7",
		creator: "user0",
		category: "chatting",
		 
		media_servers: [{
			quality: 'subsd',
			access_url: "http://localhost:10000/live/user0_subsd/index.m3u8"
		}]
	}
]

export default streams;