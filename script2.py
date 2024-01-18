import json
import os
import subprocess
import boto3

# S3_DESTINATION_BUCKET = "ffmpeg-results"
# S3_DESTINATION_BUCKET2 = "ffmpeg-hsl-results"
S3_DESTINATION_BUCKET = "ffmpeg-results-downloadable"
S3_DESTINATION_BUCKET2 = "ffmpeg-results-hsl"

def lambda_handler(event, context):

    s3_source_bucket = event['Records'][0]['s3']['bucket']['name']
    s3_source_key = event['Records'][0]['s3']['object']['key']
    
    ################
    ### script 3 ###
    ################
    
    source_link = f"https://{s3_source_bucket}.s3.ap-south-1.amazonaws.com/{s3_source_key}"
    
    # ffmpeg_command = f"/opt/bin/ffmpeg -y -i {source_link} -vf 'scale=1280:720' -c:a copy -c:v libx264 -profile:v high -level:v 4.2 -crf 18 -movflags frag_keyframe+empty_moov -f mp4 -"
    
    
    s3_source_basename = os.path.splitext(os.path.basename(s3_source_key))[0]
    # s3_destination_filename = s3_source_basename + "_720p_cli.mp4"
    
    # Check if ffmpeg is installed
    try:
        subprocess.run(['ffmpeg', '-version'], check=True)
    except FileNotFoundError:
        print("Error: FFmpeg is not installed. Please install FFmpeg on your VM.")
        return

    s3 = boto3.client('s3')
    
    destination_bucket = "ffmpeg-results"
    destination_key = f"{s3_source_basename}/720p/{s3_destination_filename}"
    
    resolutionsTuple = [
        ('640:360:flags=lanczos', '360'),
        ('854:480:flags=lanczos', '480'),
        ('1280:720:flags=lanczos', '720')
    ]

    for resolution in resolutionsTuple:
        scale, res_scale = resolution
        s3_destination_filename = f'output_{res_scale}.mp4'
        destination_key = f"{s3_source_basename}/{res_scale}/{s3_destination_filename}"
         
        ffmpeg_command = f"/opt/bin/ffmpeg -y -i {source_link} -vf 'scale={scale}' -c:a copy -c:v libx264 -profile:v high -level:v 4.2 -crf 18 -movflags frag_keyframe+empty_moov -f mp4 -"

        # Open a stream for the FFmpeg command
        with subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, shell=True) as process:
                # Upload the stream to the destination S3 bucket
                s3.upload_fileobj(process.stdout, destination_bucket, destination_key)

        print(f"Successfully converted and copied '{s3_source_key}' from '{s3_source_bucket}' to '{destination_key}' in '{destination_bucket}'.")
    return {
        'statusCode': 200,
        'body': json.dumps('Processing complete successfully')
    }