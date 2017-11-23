#Author : Pavani Boga ( pavanianapala@gmail.com )
#Date : 10/27/2017
#Job : https://www.upwork.com/jobs/~01aa35bb2697c68e53
#This script downloads the video segments from a live youtube video till you stop it, assembles and puts in mp4 container
#Run : python3.6 live.py <<youtube_live_video_link>>

from youtube_dl import YoutubeDL
import sys
import subprocess
import re
import os



def fetch_stream_url(video_url):
    ydl = YoutubeDL()
    metadata = ydl.extract_info(video_url,download=False)

    # if video is not live or does not have 720p abort it
    if metadata['is_live'] == 'False':
        print("Not a Live Video, aborting")
        sys.exit(1)

    if metadata['height'] != 720:
        print("Desired resolution not available, aborting")
        sys.exit(1)

    return metadata['url']

def capture_live(stream_url,out_dir):
    print(stream_url)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    log_handle = open('{}/ffmpeg.log'.format(out_dir),'a+')
    ffmpeg_cmd = 'nohup /usr/local/bin/ffmpeg -y -i {} -c:v copy -c:a copy -preset veryfast -f segment -segment_start_number 0 -output_ts_offset 0 -segment_time 5 -segment_time_delta 0.05 -segment_list {}/playlist.m3u8 -segment_format mpegts {}/%d.ts'.format(stream_url,out_dir,out_dir)
    print('[Starting the capture from live stream, press q to quit]')
    try:
        ffmpeg_process = subprocess.call(ffmpeg_cmd,stdout=log_handle,stderr=log_handle,shell=True)
    except KeyboardInterrupt:
        ffmpeg_process.terminate()
        print('[Live Capture Ended]')
        return

def assemble_ts(out_dir):
    print('[Concatenating all the captured stream files as mp4]')
    ts_files = [ file for file in os.listdir(out_dir) if file.endswith('.ts')]
    log_handle = open('%s/ffmpeg.log' % out_dir, 'a+')
    with open('{}/playlist.txt'.format(out_dir),'w') as f:
        for entry in sorted(ts_files, key=lambda x: int(re.search(r'(\d+)\.ts', x).group(1))):
            f.write('file \'{}\''.format(entry))
            f.write('\n')
    ffmpeg_concat = 'ffmpeg -y -safe 0 -f concat -i {}/playlist.txt -c copy {}/file.mp4'.format(out_dir,out_dir)
    try:
        subprocess.call(ffmpeg_concat,stdout=log_handle,stderr=log_handle,shell=True)
    except Exception as e:
        print(e)

def play_video(video):
    print('[Playing the mp4 file]')
    mp4_file = '/tmp/{}/file.mp4'.format(video)
    log_handle = open('/tmp/{}/ffmpeg.log'.format(video), 'a+')
    ffplay_cmd = 'ffplay {}'.format(mp4_file)
    try:
        subprocess.call(ffplay_cmd,stdout=log_handle,stderr=log_handle,shell=True)
    except Exception as e:
        print(e)




if __name__ == "__main__":
    video_url = sys.argv[1]
    video_id = re.search(r'v=(.*)',video_url).group(1)
    stream_url = fetch_stream_url(video_url)
    capture_live(stream_url,'/tmp/{}'.format(video_id))
    assemble_ts('/tmp/{}'.format(video_id))
    play_video(video_id)
