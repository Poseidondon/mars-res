from requests import get, post, delete
from pprint import pprint

pprint(get('https://9fbd909d.ngrok.io/api/v2/jobs').json())
