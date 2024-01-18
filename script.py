import boto3
import subprocess
# from boto3.s3.transfer import S3Transfer

def setup_boto():
    # Set up AWS credentials 
    boto3.setup_default_session(aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=region_name)


# Install the required library
# You can install the library using: pip install boto3

# def copy_object(source_bucket, source_key, destination_bucket, destination_key):
#     s3 = boto3.client('s3')

#     copy_source = {'Bucket': source_bucket, 'Key': source_key}

#     try:
#         s3.copy_object(Bucket=destination_bucket, CopySource=copy_source, Key=destination_key)
#         print(f"Successfully copied '{source_key}' from '{source_bucket}' to '{destination_key}' in '{destination_bucket}'.")
#     except Exception as e:
#         print(f"Error copying object: {e}")

# def convert_and_copy_video(source_bucket, source_key, destination_bucket, destination_key, source_link):
#     # Replace with your FFmpeg command
#     ffmpeg_command = f"ffmpeg -y -i {source_link} -vf 'scale=1280:720' -c:a copy -f mp4 -movflags frag_keyframe+empty_moov -"

#     # Check if ffmpeg is installed
#     try:
#         subprocess.run(['ffmpeg', '-version'], check=True)
#     except FileNotFoundError:
#         print("Error: FFmpeg is not installed. Please install FFmpeg on your VM.")
#         return

#     # Create an S3 Transfer object
#     # s3 = boto3.resource('s3')
    
#     s3 = boto3.client('s3')
#     # transfer = S3Transfer(s3.meta.client)

#     try:
#         # Open a stream for the FFmpeg command
#         with subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, shell=True) as process:
#             # Upload the stream to the destination S3 bucket
#             s3.upload_fileobj(process.stdout, destination_bucket, destination_key)

#         print(f"Successfully converted and copied '{source_key}' from '{source_bucket}' to '{destination_key}' in '{destination_bucket}'.")
#     except Exception as e:
#         print(f"Error converting and copying video: {e}")

def convert_and_copy_video(aws_access_key_id, aws_secret_access_key, region_name, source_bucket, source_key, destination_bucket, destination_key, source_link):
    
    boto3.setup_default_session(aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=region_name)
    
    # Replace with your FFmpeg command
    ffmpeg_command = f"ffmpeg -y -i {source_link} -vf 'scale=1280:720' -c:a copy -c:v libx264 -profile:v high -level:v 4.2 -crf 18 -movflags frag_keyframe+empty_moov -f mp4 -"

    # Check if ffmpeg is installed
    try:
        subprocess.run(['ffmpeg', '-version'], check=True)
    except FileNotFoundError:
        print("Error: FFmpeg is not installed. Please install FFmpeg on your VM.")
        return

    s3 = boto3.client('s3')

    try:
        # Open a stream for the FFmpeg command
        with subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, shell=True) as process:
            # Upload the stream to the destination S3 bucket
            s3.upload_fileobj(process.stdout, destination_bucket, destination_key)

        print(f"Successfully converted and copied '{source_key}' from '{source_bucket}' to '{destination_key}' in '{destination_bucket}'.")
    except Exception as e:
        print(f"Error converting and copying video: {e}")



def main():
    # Replace with your AWS credentials and bucket names
    aws_access_key_id = 'AKIAZNCOHASC3YHEHV4E'
    aws_secret_access_key = 'pwhwlUc8Yj82cI1g7chQMYdwjGcyIH60GgguJ6/4'
    region_name = 'ap-south-1'
    
    source_bucket = 'ffmpeg-adventures'
    destination_bucket = 'ffmpeg-results'
    source_key = '1minlofi.mp4'
    destination_key = 'file_example_MP4_640_3MG_720p_from_cli_v2.mp4'
    source_link = 'https://ffmpeg-adventures.s3.ap-south-1.amazonaws.com/Restaurant.mp4'

    # # Set up AWS credentials
    # boto3.setup_default_session(aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=region_name)

    # Copy the original video to the destination bucket
    # copy_object(source_bucket, source_key, destination_bucket, destination_key)

    # Convert and copy the video in the destination bucket
    convert_and_copy_video(aws_access_key_id, aws_secret_access_key, region_name,destination_bucket, destination_key, destination_bucket, destination_key, source_link)

if __name__ == "__main__":
    main()
