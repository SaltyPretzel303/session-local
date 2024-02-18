export type MediaServer = {
	ip: string
	port: number
	media_path: string
	full_path: string
}

export type StreamInfo = {
	title: string
	creator: string
	category: string
	viewers: number
	media_server: MediaServer
}