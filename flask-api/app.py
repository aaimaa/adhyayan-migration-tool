from flask import Flask, request, jsonify
from flask_cors import CORS  

from ffmpeg_convertor import convert_video_resolution
from ffmpeg_convertor import convert_video_hls
from ffmpeg_convertor import upload_to_s3

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def hello():
    return '<h1>This is the api for converting a video url to a different aspect ratio!</h1>'

@app.route('/upload', methods=['POST'])
def upload_endpoint():
    try:
        data = request.get_json()
        aws_access_key_id = data['aws_access_key_id']
        aws_secret_access_key = data['aws_secret_access_key']
        region_name = data['region_name']
        destination_bucket = data['destination_bucket']
        source_link = data['source_link']
        
        result = upload_to_s3(destination_bucket=destination_bucket, source_url=source_link, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=region_name)
        
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/convert-resolution', methods=['POST'])
def convertor_endpoint():
    try:
        data = request.get_json()
        aws_access_key_id = data['aws_access_key_id']
        aws_secret_access_key = data['aws_secret_access_key']
        region_name = data['region_name']
        destination_bucket = data['destination_bucket']
        source_link = data['source_link']
        
        result = convert_video_resolution(destination_bucket=destination_bucket, source_link=source_link, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=region_name)
        
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/convert-hls', methods=['POST'])
def convertor_endpoint_hls():
    try:
        data = request.get_json()
        aws_access_key_id = data['aws_access_key_id']
        aws_secret_access_key = data['aws_secret_access_key']
        region_name = data['region_name']
        destination_bucket = data['destination_bucket']
        source_link = data['source_link']
        
        result = convert_video_hls(destination_bucket=destination_bucket, source_link=source_link, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=region_name)
        
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)