import requests
from xml.etree import cElementTree as ET
# namespaces = {
#     'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
#     'a': 'http://api.chartlyrics.com',
# }


def chart_lyrics(artist, song):
    params = {'artist': artist, 'song': song}
    url1 = 'http://api.chartlyrics.com/apiv1.asmx/SearchLyricDirect'
    res1 = requests.get(url=url1, params=params)
    lyric_text = res1.text
    listed = lyric_text.split()
    listoflyrics = []

    foo = False
    for word in listed:
        if not foo:
            if '<Lyric>' in word:
                foo = True
                listoflyrics.append(word)
        elif '</Lyric>' in word:
            foo = False
        else:
            listoflyrics.append(word)

    print(listoflyrics)
    final = ' '.join(listoflyrics)
    print(final)
    print('Output file created')

    return


artist = 'Michael Jackson'
song = 'Thriller'
chart_lyrics(artist, song)
