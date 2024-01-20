import boto3
import subprocess
import os

import requests

def upload_to_s3(aws_access_key_id, aws_secret_access_key, region_name, destination_bucket, source_url):
    # Extract the filename from the URL
    file_name = source_url.split('/')[-1]

    boto3.setup_default_session(aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=region_name)

    # Initialize S3 client
    s3 = boto3.client('s3')

    try:
        # Stream the file content directly from the URL
        response = requests.get(source_url, stream=True)
        if response.status_code == 200:
            # Upload the streaming content to S3
            s3.upload_fileobj(response.raw, destination_bucket, file_name)
            print(f"Successfully streamed and uploaded '{file_name}' to '{destination_bucket}'.")
        else:
            print(f"Failed to fetch the file from the URL. HTTP Status Code: {response.status_code}")
    except Exception as e:
        print(f"Error uploading file to S3: {e}")

def upload_to_r2(aws_access_key_id, aws_secret_access_key, region_name, destination_bucket, source_url, endpoint_url):
    # Extract the filename from the URL
    file_name = source_url.split('/')[-1]

    # Initialize S3 client with custom endpoint
    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=region_name, endpoint_url=endpoint_url)

    try:
        # Stream the file content directly from the URL
        response = requests.get(source_url, stream=True)
        if response.status_code == 200:
            # Upload the streaming content to R2
            s3.upload_fileobj(response.raw, destination_bucket, file_name)
            print(f"Successfully streamed and uploaded '{file_name}' to '{destination_bucket}'.")
        else:
            print(f"Failed to fetch the file from the URL. HTTP Status Code: {response.status_code}")
    except Exception as e:
        print(f"Error uploading file to R2: {e}")
    
def convert_video_resolution(aws_access_key_id, aws_secret_access_key, region_name, destination_bucket, source_link):
    
    split_str = source_link.split('/')
    s3_source_bucket = split_str[2].split('.')[0]
    s3_source_key = split_str[3]
    s3_source_basename = split_str[3].split('.')[0]
    
    boto3.setup_default_session(aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=region_name)

    # Check if ffmpeg is installed
    try:
        subprocess.run(['ffmpeg', '-version'], check=True)
    except FileNotFoundError:
        print("Error: FFmpeg is not installed. Please install FFmpeg on your VM.")
        return

    s3 = boto3.client('s3')
    
    resolutionsTuple = [
        ('426:240:flags=lanczos', '240'),
        ('640:360:flags=lanczos', '360'),
        ('854:480:flags=lanczos', '480'),
        ('1280:720:flags=lanczos', '720')
    ]
    
    try: 
        for resolution in resolutionsTuple:
            scale, res_scale = resolution
            s3_destination_filename = f'output_{res_scale}.mp4'
            destination_key = f"{s3_source_basename}/{res_scale}/{s3_destination_filename}"
            
            ffmpeg_command = f"ffmpeg -y -i {source_link} -vf 'scale={scale}' -c:a copy -c:v libx264 -profile:v high -level:v 4.2 -crf 18 -movflags frag_keyframe+empty_moov -f mp4 -"

            # try:
            # Open a stream for the FFmpeg command
            with subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, shell=True) as process:
                    # Upload the stream to the destination S3 bucket
                    s3.upload_fileobj(process.stdout, destination_bucket, destination_key)

            print(f"Successfully converted and copied '{s3_source_key}' from '{s3_source_bucket}' to '{destination_key}' in '{destination_bucket}'.")
    except Exception as e:
        print(f"Error converting video: {e}")
   
def convert_video_resolution_r2(aws_access_key_id, aws_secret_access_key, region_name, destination_bucket, source_link, endpoint_url):
    
    s3_source_basename = source_link.split('/')[-1].split('.')[0]
    
    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=region_name, endpoint_url=endpoint_url)
    
    # Check if ffmpeg is installed
    try:
        subprocess.run(['ffmpeg', '-version'], check=True)
    except FileNotFoundError:
        print("Error: FFmpeg is not installed. Please install FFmpeg on your VM.")
        return
    
    resolutionsTuple = [
        ('426:240:flags=lanczos', '240'),
        ('640:360:flags=lanczos', '360'),
        ('854:480:flags=lanczos', '480'),
        ('1280:720:flags=lanczos', '720')
    ]
    
    try: 
        for resolution in resolutionsTuple:
            scale, res_scale = resolution
            s3_destination_filename = f'output_{res_scale}.mp4'
            destination_key = f"{s3_source_basename}/{res_scale}/{s3_destination_filename}"
            
            ffmpeg_command = f"ffmpeg -y -i {source_link} -vf 'scale={scale}' -c:a copy -c:v libx264 -profile:v high -level:v 4.2 -crf 18 -movflags frag_keyframe+empty_moov -f mp4 -"

            # try:
            # Open a stream for the FFmpeg command
            with subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, shell=True) as process:
                    # Upload the stream to the destination S3 bucket
                    s3.upload_fileobj(process.stdout, destination_bucket, destination_key)

            print(f"Successfully converted and copied '{source_link}' to '{destination_key}' in '{destination_bucket}'.")
    except Exception as e:
        print(f"Error converting video: {e}")

def convert_video_hsl(aws_access_key_id, aws_secret_access_key, region_name, destination_bucket, source_link, endpoint_url):
    print("Current working directory:", os.getcwd())
    try:
        # Check if FFmpeg is installed
        subprocess.run(['ffmpeg', '-version'], check=True)
    except subprocess.CalledProcessError:
        raise Exception("Error: FFmpeg is not installed. Please install FFmpeg on your VM.")
    except FileNotFoundError:
        raise Exception("Error: FFmpeg is not installed. Please install FFmpeg on your VM.")

    split_str = source_link.split('/')
    # s3_source_key = split_str[3]
    s3_source_basename = split_str[-1].split('.')[0]
    
    if endpoint_url == '':
        s3_client = boto3.client(
            service_name="s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )
    else:
        s3_client = boto3.client(
            service_name="s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
            endpoint_url=endpoint_url
        )

    resolution_dict = {
        '720p': "1280:720",
        '360p': "640:360",
        '480p': "854:480",
        '240p': "426:240"
    }

    resolutions = ['360p', '480p', '720p', '240p']
    
    for resolution in resolutions:
        os.makedirs(f'{resolution}_output', exist_ok=True)

    for resolution in resolutions:
        output_playlist = f'{resolution}_output/out.m3u8'
        ffmpeg_command = f'ffmpeg -y -i {source_link} -vf "scale={resolution_dict[resolution]}" -c:v h264 -hls_time 10 -hls_list_size 0 -hls_flags single_file -f hls -c:a aac -strict experimental -b:a 192k -hls_playlist_type vod -hls_segment_type fmp4 {output_playlist}'

        print(f"Running FFmpeg command: {ffmpeg_command}")
        result = subprocess.run(ffmpeg_command, shell=True, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0:
            print(f"Error running FFmpeg:\n{result.stderr}")
            raise Exception("Error running FFmpeg.")

        temp_folder_path = os.path.join(os.getcwd(), f'{resolution}_output')

        files = os.listdir(temp_folder_path)

        # Upload each file to S3
        for file in files:
            file_path = os.path.join(temp_folder_path, file)

            # Read the file content
            with open(file_path, 'rb') as file_content:
                # Specify the S3 key (object key)
                s3_key = f'{s3_source_basename}/{resolution}/{file}'

                # Upload the file to S3
                s3_client.upload_fileobj(file_content, destination_bucket, s3_key)

                print(f'File {file} uploaded to S3.')

            # Remove the file after successful upload
            try:
                os.remove(file_path)
                print(f'File {file} removed.')
            except Exception as e:
                print(f"Error removing file {file}: {e}")
        
    for resolution in resolutions:
        os.rmdir(f'{resolution}_output')
        print(f'Directory {resolution}_output removed.')

    print("Operation successful")


def main():
    print('hello, from ffmpeg_convertor function')

if __name__ == "__main__":
    main()
