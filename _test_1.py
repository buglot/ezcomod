import requests

download_url = "http://192.168.1.190:4000/peter.zip"
response = requests.get(download_url, stream=True)

total_size = int(response.headers.get('content-length', 0))
print("ขนาดทั้งหมด:", total_size)