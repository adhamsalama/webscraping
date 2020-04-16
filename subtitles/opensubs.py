# For downloading subtitles from opensubtitles.org
# No APIs. We web scrap like real men.

import requests
from bs4 import BeautifulSoup
import os
import zipfile

movie = input('Movie name: ')
lang = input('Language(Abbreviation): ')

r = requests.get('https://www.imdb.com/find?q=' + movie)
if r.status_code != 200:
    print(r.status_code)
    exit(1)

soup = BeautifulSoup(r.text, 'html.parser')

results = soup.find('table', {'class': 'findList'})


rows = results.findAll('tr', {'class': 'findResult'})

flag = False
for row in rows:
    innerhtml = row.find('td', {'class': 'result_text'})
    movie_name = innerhtml.text.strip()
    ans = input('Is your movie "' + movie_name + '"?\n')
    if ans.lower() == ('y' or 'yes'):
        flag = True
        break
if not flag:
    print("Sorry mate I couldn't find it")
    exit(1)

result = innerhtml.find('a')

link = result.attrs['href']

imbd_id = link[7:]

opensubs = requests.get('https://www.opensubtitles.org/en/search/imdbid-' + imbd_id + '/sublanguageid-' + lang)
if opensubs.status_code != 200:
    print(opensubs.status_code, "Can't find movie on opensubs")
    exit(1)

opensubs = BeautifulSoup(opensubs.text, 'html.parser')
subs_table = opensubs.find('table', {'id': 'search_results'})

tr = subs_table.findAll('tr')[1]

strong = tr.find('strong')

link = 'https://www.opensubtitles.org' + strong.find('a').attrs['href']
print(link)

download_page = requests.get(link)
download_page.raise_for_status()

download_link = BeautifulSoup(download_page.text, 'html.parser').find('a', {'title': 'Download'}).attrs['href']
print(download_link)

sub = requests.get(download_link, headers={'referer': link})
# Save zipfile
movie_name = movie_name.replace(':', '')

# Create a folder for subtitle
folder = input('Download folder: ')
if folder:
    os.chdir(folder)

with open(movie_name.replace(' ', '_') + '.zip', 'wb') as f:
    f.write(sub.content)

# Unzip zipfile
with zipfile.ZipFile(movie_name.replace(' ', '_') + '.zip') as zip:
    zip.extractall()

# Delete zipfile
os.remove(movie_name.replace(' ', '_') + '.zip')

print("Success!")
