import requests
import json
from utils import load_config

def get_nasa_picture():
    config = load_config('../nasa_credentials.yml')
    key = config['key']
    response_API = requests.get(f'https://api.nasa.gov/planetary/apod?api_key={key}')
    data = response_API.text
    json_data = json.loads(data)
    return json_data['url']

if __name__ == '__main__':
    print(get_nasa_picture())