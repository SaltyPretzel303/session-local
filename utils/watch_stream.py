import sys
from ffpyplayer.player import MediaPlayer


PLAYER_WIDTH = 450
PLAYER_HEIGHT = 400
DEFAULT_STREAM_URL = "http://localhost:8000/live/mystream/index.m3u8"


def watch_stream(stream_url, w, h ):
	player = MediaPlayer(filename = stream_url)	
	player.play()


if __name__ == "__main__":

	stream_url = DEFAULT_STREAM_URL
	if len(sys.argv) == 2:
		print("Using passed argument ... ")
		stream_url = sys.argv[1]

	print(f"Watching: {stream_url}")
	watch_stream(stream_url, PLAYER_WIDTH, PLAYER_HEIGHT)


	input("Press Enter to close stream...")
