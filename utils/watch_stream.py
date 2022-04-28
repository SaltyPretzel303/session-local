import sys
import vlc

DEFAULT_STREAM_URL = "http://localhost:9992/hlsstream/stream.m3u8"


def watch_stream(stream_url):
    if stream_url == None or stream_url == "":
        stream_url = DEFAULT_STREAM_URL

    Instance = vlc.Instance()
    player = Instance.media_player_new()
    Media = Instance.media_new(stream_url)
    Media.get_mrl()
    player.set_media(Media)
    player.play()


if __name__ == "__main__":

    stream_url = DEFAULT_STREAM_URL
    if len(sys.argv) == 1:
        stream_url = sys.argv[1]

    watch_stream(stream_url)

    input("Press Enter to close stream...")
