import requests
import json

def get_nasa_picture():
    response_API = requests.get('https://api.nasa.gov/planetary/apod?api_key=Vi7YtJYtBC8nHyVlOGrKVFg9QzYTj5iqSTVwgSg7')
    data = response_API.text
    json_data = json.loads(data)
    return json_data['url']

if __name__ == '__main__':
    print(get_nasa_picture())