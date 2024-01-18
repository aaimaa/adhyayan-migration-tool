# URL to HLS convertor &  uploader, URL to resolution convertor, URL to s3 uploader

## About

This repo contains a simple python api that converts a given video source url :
- ```\convert-resolution``` to different resolutions & then uploads directly to your s3 storage
- ```\convert-hls``` to hls format (gives a master m3u8 file & a m4s file) and uploads it directly to your s3 storage
- ```\upload``` and uploads it to your s3 storage

## setup

Run the below command to download the dependencies: 
```
pip install -r requirements.txt
```

After installing requisite dependencies, do: 
```python3 app.py```

*To test this api or run this api on your server, don't forget to install ffmpeg*

Api will be run on http://127.0.0.1:5000

## 