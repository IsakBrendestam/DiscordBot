import imp
import requests

from utils import load_config, save_config

def authorize():
        #getting credentials
    config = load_config('../reddit_credentials.yml')

    auth = requests.auth.HTTPBasicAuth(config['ClienntId'], config['SecretToken'])

    data = {'grant_type': 'password',
            'username': config['UserName'],
            'password': config['UserPassword']}

    headers = {'User-Agent': 'MyBot/0.0.1'}

    res = requests.post('https://www.reddit.com/api/v1/access_token',
                    auth=auth, data=data, headers=headers)

    #Getting acces token
    token = res.json()['access_token']

    config['access_token'] = token

    save_config(config, '../reddit_credentials.yml')

def get_headers():
    config = load_config('../reddit_credentials.yml')
    headers = {'User-Agent': 'MyBot/0.0.1'}
    return {**headers, **{'Authorization': f"bearer {config['access_token']}"}}

def get_request_json(link):
    try:
        return requests.get(link, headers=get_headers()).json()
    except:
        authorize()
        return requests.get(link, headers=get_headers()).json()

    

def get_subreddit(sub, order_by):
    #requesting from subreddit
    return get_request_json(f'https://oauth.reddit.com/r/{sub}/{order_by}')

def get_me():
    return get_request_json(f"https://oauth.reddit.com/api/v1/me")

def get_user(name):
    return get_request_json(f"https://oauth.reddit.com/user/{name}/about")

def get_pic_posts(sub, order_by, nsfw):
    res = get_subreddit(sub, order_by)

    post_data = []

    #check if res is correct
    if not 'data' in res:
        return None

    for post in res['data']['children']:
        #loops over posts
        if 'data' in post:
            if not post['data']['over_18'] ^ nsfw:
                image_url = post['data']['url']
                if image_url:
                    post_data.append(post['data'])
            else:
                post_data.append(None)

    if not post_data:
        return None

    return post_data


if __name__ == '__main__':
    authorize()
