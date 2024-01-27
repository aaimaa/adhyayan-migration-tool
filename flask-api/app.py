import os
from datetime import datetime
import csv

from werkzeug.utils import secure_filename

from flask import Flask, request, jsonify

from flask_socketio import SocketIO

from flask_cors import CORS  
import pandas as pd
from io import StringIO

from ffmpeg_convertor import convert_video_resolution
from ffmpeg_convertor import convert_video_resolution_r2
from ffmpeg_convertor import convert_video_hsl
from ffmpeg_convertor import upload_to_s3
from ffmpeg_convertor import upload_to_r2

app = Flask(__name__)
CORS(app, resources={r"*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/', methods=['GET'])
def hello():
    html = '''<h1>Video Operations API</h1>

    <section>
        <h2>About</h2>
        <p>This repo contains a simple Python API that converts a given video source URL:</p>
        <ul>
            <li><code>/convert-resolution</code> - Converts to different resolutions & uploads directly to your S3 storage.</li>
            <li><code>/convert-hls</code> - Converts to HLS format and uploads it directly to your S3 storage.</li>
            <li><code>/upload</code> - Uploads the video directly to your S3 storage.</li>
        </ul>
    </section>
'''
    return html

@app.route('/upload', methods=['POST'])
def upload_endpoint():
    try:
        data = request.get_json()
        print("recieved data: ", data)
        aws_access_key_id = data['aws_access_key_id']
        aws_secret_access_key = data['aws_secret_access_key']
        region_name = data['region_name']
        destination_bucket = data['destination_bucket']
        source_link = data['source_link']
        
        endpoint_url = data['endpoint_url']
        
        if endpoint_url.strip() == "":
            result = upload_to_s3(destination_bucket=destination_bucket, source_url=source_link, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=region_name)
        else:
            result = upload_to_r2(destination_bucket=destination_bucket, source_url=source_link, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=region_name, endpoint_url=endpoint_url)
            
        socketio.emit('operation_complete', {'result': result, 'link': source_link})
        
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/upload-csv', methods=['POST'])
def upload_csv_endpoint():
    try:
        data = request.form.to_dict()
        print(f"to debug upload_to_r2: {data}")
        aws_access_key_id = data['aws_access_key_id']
        aws_secret_access_key = data['aws_secret_access_key']
        region_name = data['region_name']
        destination_bucket = data['destination_bucket']
        endpoint_url = data['endpoint_url']

        # Check if 'csv_file' is provided
        if 'csv_file' in request.files:
            csv_file = request.files['csv_file']
            csv_content = csv_file.read().decode('utf-8')
            df = pd.read_csv(StringIO(csv_content), header=None)
            source_links = df[0].tolist()
            
            filename = secure_filename(csv_file.filename).split('.')[0]
            
            current_datetime = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
            csv_filename = f"{current_datetime}_{filename}_upload_results.csv"
            user_home = os.path.expanduser("~")
            csv_filepath = os.path.join(user_home, "file_reports", csv_filename)

            result = []
            for source_link in source_links:
                try: 
                    if endpoint_url.strip() == "":
                        success = upload_to_s3(destination_bucket=destination_bucket, source_url=source_link, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=region_name)
                    else:
                        success = upload_to_r2(destination_bucket=destination_bucket, source_url=source_link, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=region_name, endpoint_url=endpoint_url)
                    
                    with open(csv_filepath, 'a', newline='') as csv_file:
                        csv_writer = csv.writer(csv_file)
                        csv_writer.writerow([source_link, success])
                    
                    result.append({'link': source_link, 'success': success})
                    socketio.emit('operation_complete', {'link': source_link, 'success': success})
                except Exception as e: 
                    print(f"Error uploading {source_link}: {e}")
                    result.append({'link': source_link, 'success': False})

                    with open(csv_filepath, 'a', newline='') as csv_file:
                        csv_writer = csv.writer(csv_file)
                        csv_writer.writerow([source_link, success])
                    
                    socketio.emit('operation_complete', {'link': source_link, 'success': False})

            return jsonify({'result': result})
        else:
            return jsonify({'error': 'CSV file not provided'})

    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/convert-resolution', methods=['POST'])
def convertor_endpoint():
    try:
        data = request.get_json()
        print('data after getting it on server: ', data)
        aws_access_key_id = data['aws_access_key_id']
        aws_secret_access_key = data['aws_secret_access_key']
        region_name = data['region_name']
        destination_bucket = data['destination_bucket']
        source_link = data['source_link']
        
        endpoint_url = data['endpoint_url']
        
        if endpoint_url.strip() == "":
            result = convert_video_resolution(destination_bucket=destination_bucket, source_link=source_link, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=region_name)
        else:
            result = convert_video_resolution_r2(destination_bucket=destination_bucket, source_link=source_link, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=region_name,endpoint_url=endpoint_url)
        
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)})
    

@app.route('/convert-resolution-csv', methods=['POST'])
def convertor_csv_endpoint():
    try:
        data = request.form.to_dict()
        aws_access_key_id = data['aws_access_key_id']
        aws_secret_access_key = data['aws_secret_access_key']
        region_name = data['region_name']
        destination_bucket = data['destination_bucket']
        
        endpoint_url = data['endpoint_url']

        if 'csv_file' in request.files:
            csv_file = request.files['csv_file']
            csv_content = csv_file.read().decode('utf-8')
            df = pd.read_csv(StringIO(csv_content), header=None)
            source_links = df[0].tolist()
            
            filename = secure_filename(csv_file.filename).split('.')[0]
            
            current_datetime = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
            csv_filename = f"{current_datetime}_{filename}_resolution_conversion_results.csv"
            user_home = os.path.expanduser("~")
            csv_filepath = os.path.join(user_home, "file_reports", csv_filename)
        else:
            return jsonify({'error': 'CSV file not provided'})

        result = []
        for source_link in source_links:
            try:
                if endpoint_url.strip() == "":
                    success = convert_video_resolution(destination_bucket=destination_bucket, source_link=source_link, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=region_name)
                else:
                    success = convert_video_resolution_r2(destination_bucket=destination_bucket, source_link=source_link, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=region_name,endpoint_url=endpoint_url)
                
                with open(csv_filepath, 'a', newline='') as csv_file:
                        csv_writer = csv.writer(csv_file)
                        csv_writer.writerow([source_link, success])
                
                result.append({'link': source_link, 'success': success})
                socketio.emit('operation_complete', {'link': source_link, 'success': success})
            except Exception as e:
                print(f"Error uploading {source_link}: {e}")
        
                result.append({'link': source_link, 'success': False})

                with open(csv_filepath, 'a', newline='') as csv_file:
                    csv_writer = csv.writer(csv_file)
                    csv_writer.writerow([source_link, False])
                            
                socketio.emit('operation_complete', {'link': source_link, 'success': False})
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/convert-hsl', methods=['POST'])
def convertor_endpoint_hsl():
    try:
        data = request.get_json()
        aws_access_key_id = data['aws_access_key_id']
        aws_secret_access_key = data['aws_secret_access_key']
        region_name = data['region_name']
        destination_bucket = data['destination_bucket']
        source_link = data['source_link']
        
        endpoint_url = data['endpoint_url']
        
        result = convert_video_hsl(destination_bucket=destination_bucket, source_link=source_link, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=region_name, endpoint_url=endpoint_url)
        
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/convert-hsl-csv', methods=['POST'])
def convertor_csv_hsl_endpoint():
    try:
        data = request.form.to_dict()
        aws_access_key_id = data['aws_access_key_id']
        aws_secret_access_key = data['aws_secret_access_key']
        region_name = data['region_name']
        destination_bucket = data['destination_bucket']
        endpoint_url = data['endpoint_url']

        # Check if 'csv_file' is provided
        if 'csv_file' in request.files:
            csv_file = request.files['csv_file']
            csv_content = csv_file.read().decode('utf-8')
            df = pd.read_csv(StringIO(csv_content), header=None)
            source_links = df[0].tolist()
            
            filename = secure_filename(csv_file.filename).split('.')[0]
                
            current_datetime = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
            csv_filename = f"{current_datetime}_{filename}_hsl_results.csv"
            user_home = os.path.expanduser("~")
            csv_filepath = os.path.join(user_home, "file_reports", csv_filename)
        else:
            return jsonify({'error': 'CSV file not provided'})

        result = []
        for source_link in source_links:
            try:
                success = convert_video_hsl(destination_bucket=destination_bucket,
                                            source_link=source_link,
                                            aws_access_key_id=aws_access_key_id,
                                            aws_secret_access_key=aws_secret_access_key,
                                            region_name=region_name,
                                            endpoint_url=endpoint_url)
                result.append({'link': source_link, 'success': success})
                
                with open(csv_filepath, 'a', newline='') as csv_file:
                        csv_writer = csv.writer(csv_file)
                        csv_writer.writerow([source_link, success])
                
                socketio.emit('operation_complete', {'link': source_link, 'success': success})
            except Exception as e:
                print(f"error: {e}")
                result.append({'link': source_link, 'success': success})
                
                with open(csv_filepath, 'a', newline='') as csv_file:
                        csv_writer = csv.writer(csv_file)
                        csv_writer.writerow([source_link, success])
                    
                socketio.emit('operation_complete', {'link': source_link, 'success': False})
        return jsonify({'result': result})
    except Exception as e:
        print(f"error: {e}")
        result.append({'link': source_link, 'success': success})
                
        with open(csv_filepath, 'a', newline='') as csv_file:
                        csv_writer = csv.writer(csv_file)
                        csv_writer.writerow([source_link, success])
                    
        socketio.emit('operation_complete', {'link': source_link, 'success': False})
        return jsonify({'error': str(e)})

if __name__ == '__main__':
     socketio.run(app, debug=True)