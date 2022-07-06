import requests

url = 'https://en.wikipedia.org/wiki/Special:Random'

response = requests.get(url)

with open('wiki.html', 'w') as f:
    f.write(response.text)