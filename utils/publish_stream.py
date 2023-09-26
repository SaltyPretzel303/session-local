import sys

import ffmpeg

DEFAULT_STREAM_NAME = 'stream'
DEFAULT_VIDEO_PATH = '/home/nemanja/Videos/rabbit.mp4'
DEFAULT_INGEST_URL = 'rtmp://localhost:9991/live/' + DEFAULT_STREAM_NAME


def publish_stream(video_path, ingest_path, stream_name):

    if video_path == None or video_path == "":
        video_path = DEFAULT_VIDEO_PATH

    if ingest_path == None or ingest_path == "":
        ingest_path = DEFAULT_INGEST_URL

    if stream_name == None or stream_name == "":
        stream_name = DEFAULT_STREAM_NAME

    process = (
        ffmpeg
        .input(video_path)
        .output(
            ingest_path,
            codec="copy",  # use same codecs of the original video
            f='flv',  # force format
            flvflags="no_duration_filesize",
            # ^ will prevent: 'Failed to update header with correct duration.'
            # https://stackoverflow.com/questions/45220915

            # loop="-1", # questionable does this works
            # vcodec='libx264',
            # pix_fmt='yuv420p',
            # preset='veryfast',
            # r='20',
            # g='50',
            # video_bitrate='1.4M',
            # maxrate='2M',
            # bufsize='2M',
            # segment_time='6' # don't know what is this, maybe delay or buffer_size ?
        )
        .global_args("-re")  # argument to act as a live stream
        .run_async()
    )

    return process  # I guess this is what I want to return ... ?


if __name__ == "__main__":

    video_path = DEFAULT_VIDEO_PATH
    ingest_path = DEFAULT_INGEST_URL
    stream_name = DEFAULT_STREAM_NAME

    if len(sys.argv) == 3:
        video_path = sys.argv[1]
        ingest_path = sys.argv[2]
        stream_name = sys.argv[3]

    process = publish_stream(video_path, ingest_path, stream_name)
    input("Press Enter to stop stream ...")
