from dataclasses import dataclass

@dataclass
class MediaServerInfo:
	quality: str
	access_url: str
	# ^ Full access url, ready for hls player. 
	# format: rtmp://ip:port/live/streamer_quality/index.m3u8
