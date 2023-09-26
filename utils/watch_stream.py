import sys
import vlc

LOCAL_STREAM = "/home/nemanja/Videos/rabbit.mp4"
REMOTE_STREAM = "http://localhost:9992/hlsstream/stream.m3u8"

DEFAULT_STREAM_URL = REMOTE_STREAM
# DEFAULT_STREAM_URL = LOCAL_STREAM


def watch_stream(stream_url):
    if stream_url == None or stream_url == "":
        stream_url = DEFAULT_STREAM_URL

    print(f"watching : {stream_url}")

    Instance = vlc.Instance()
    player = Instance.media_player_new()
    Media = Instance.media_new(stream_url)
    Media.get_mrl()
    player.set_media(Media)
    player.play()


if __name__ == "__main__":

    stream_url = DEFAULT_STREAM_URL
    print(sys.argv)
    if len(sys.argv) == 2:
        stream_url = sys.argv[1]

    watch_stream(stream_url)

    input("Press Enter to close stream...")
