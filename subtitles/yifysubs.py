# For downloading subtitles from yifysubtitles.com
# No APIs. We web scrap like real men.

import requests
from bs4 import BeautifulSoup
import os
import zipfile

movie = input('Movie name: ').strip()
lang = input('Language: ')

# Get IMDB ID
r = requests.get('https://www.imdb.com/find?q=' + movie)
if r.status_code != 200:
    print(r.status_code)
    exit(1)
soup = BeautifulSoup(r.text, 'html.parser')

results = soup.find('table', {'class': 'findList'})


rows = results.findAll('tr', {'class': 'findResult'})

flag = False
for row in rows:
    firstrow = row
    innerhtml = firstrow.find('td', {'class': 'result_text'})
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

num = link[7:]

# Search yifysubtitles
yify = requests.get('https://www.yifysubtitles.com/movie-imdb/' + num)
if yify.status_code != 200:
    print(yify.status_code, "Can't find movie on yify")
    exit(1)

yify = BeautifulSoup(yify.text, 'html.parser')
subs_table = yify.find('table', {'other-subs'})

td = subs_table.findAll('td', {'class': 'flag-cell'})

spans = subs_table.findAll('span', {'class': 'sub-lang'})

# Search for the first result of subtitles languages
for i in range(len(spans)):
    if spans[i].text.lower() == lang:
        tr = spans[i].parent.parent
        break

# Get download link
download_cell = tr.find('td', {'class': 'download-cell'})
download_link = download_cell.find('a').attrs['href']

# Get the download page
download_page = requests.get('https://www.yifysubtitles.com/' + download_link)        
download_link = BeautifulSoup(download_page.text, 'html.parser').find('a', {'class': 'download-subtitle'}).attrs['href']

# Get zipfile
sub = requests.get(download_link)
if sub.status_code != 200:
    print(sub.status_code, "Can't find download link")
    exit(1)

movie_name = movie_name.replace(':', '')

# Create a folder for subtitle
folder = input('Download folder: ')
if folder:
    os.chdir(folder)

# Save zipfile
with open(movie_name.replace(' ', '_') + '.zip', 'wb') as f:
    f.write(sub.content)

# Unzip zipfile
with zipfile.ZipFile(movie_name.replace(' ', '_') + '.zip') as zip:
    zip.extractall()

# Delete zipfile
os.remove(movie_name.replace(' ', '_') + '.zip')

print("Success!")
