import requests
import os
import json
import random
from typing import Union

def get_random_birthday_meme() -> Union[bool, str]:
	url = 'https://api.giphy.com/v1/gifs/search'
	headers = {
		'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
	}
	params = {
		'api_key': os.getenv('MEMES_API_KEY'),
		'q': 'happy birthday'
	}

	if not params.get('api_key'): # api key not set
		print("MEMES_API_KEY not set!")
		return False

	res = requests.get(url, params=params, headers=headers)
	if res.status_code != 200:
		print(f"Fail to request from {res.url}")
		return False
	meme_embed_urls = [meme_info['embed_url'] for meme_info in json.loads(res.text)['data']]
	return random.choice(meme_embed_urls)
