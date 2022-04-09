import ffmpeg
import requests
import os
import jsonpickle
from shared_model.ingest_info import IngestInfo

VIDEO_PATH = '/home/nemanja/Videos/sample_video.mp4'
INGEST_PATH = 'rtmp://172.17.0.2:9991/live/stream'

API_URL = 'http://localhost:8000/create?user_id=user_id_1&stream_title=stream_title_1'

# this should do the same thing as ../publish_stream.sh but somehow it doesn't work
# process = (
#     ffmpeg
#     .input(VIDEO_PATH)
#     .output(
#         INGEST_PATH,
#         codec="copy",  # use same codecs of the original video
#         f='flv',
#         # vcodec='libx264',
#         # pix_fmt='yuv420p',
#         # preset='veryfast',
#         # r='20',
#         # g='50',
#         # video_bitrate='1.4M',
#         # maxrate='2M',
#         # bufsize='2M',
#         segment_time='6')
#     .global_args("-re")  # argument to act as a live stream
#     .run_async()
# )

response = requests.get(API_URL)

if response.status_code != 200:
    print("Ingest request failed")
    print("Response: " + str(response.status_code))
    print("Streamer exiting ... ")

    exit(1)

json_response: IngestInfo = jsonpickle.decode(response.content)

print("Ingest request was successful")
print("Will stream video ... ")

ingest_address = 'rtmp://' + json_response.ip + ':' + \
    str(json_response.port) + '/' + json_response.stream_key

os.system('../publish_stream.sh ' + VIDEO_PATH + ' ' + ingest_address)
