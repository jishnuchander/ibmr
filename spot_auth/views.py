from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponse
import sys
import json
import spotipy
import spotipy.util as util
import requests
import pusher
import time
from .tasks import pusher_task, lyrics, song_suggestions
import random
import string
from SentimentAnalysis import Sentiment_Analysis as sa
from azlyrics.azlyrics import lyrics
# Create your views here.
client_id = "client_id"
client_secret = "client_secret"
lyrics_api_key = "lyrics_api_key"
pusher_client = pusher.Pusher(
    app_id='app_id',
    key='key',
    secret='secret',
    cluster='cluster',
    ssl=True
)


def index(request):
    return render(request, 'spot-auth/main.html')


def mob_view(request):
    return render(request, 'spot-auth/mob_home.html')


def upload(request):
    return render(request, 'spot-auth/upload.html')


def web_view(request):
    return render(request, 'spot-auth/auth.html', {'image': False})


def show_tracks(tracks):
    for i, item in enumerate(tracks['items']):
        track = item['track']
        print("   %d %32.32s %s" % (i, track['artists'][0]['name'],
                                    track['name']))


def callback(request):

    code = request.GET.get("code")
    url = "https://accounts.spotify.com/api/token"
    grant_type = "authorization_code"
    redirect_uri = "http://127.0.0.1:8000/callback/"
    client = {'client_id': client_id, 'client_secret': client_secret,
              'grant_type': grant_type, 'redirect_uri': redirect_uri, 'code': code}
    res = requests.post(url, data=client)
    r_json = res.json()
    access_token = r_json['access_token']
    token_type = r_json['token_type']
    scope = r_json['scope']
    expires_in = r_json['expires_in']
    refresh_token = r_json['refresh_token']
    if access_token:
        sp = spotipy.Spotify(auth=access_token)
        user = sp.current_user()
        user_name = user['display_name']
        user_profile = user['external_urls']['spotify']
        user_id = user['id']
        img_uri = user['images'][0]['url']
        playlist = sp.playlist('2YRe7HRKNRvXdJBp9nXFza', fields="tracks,next")
        tracks = playlist['tracks']
        lyrics.delay(user_name, user_id, img_uri, tracks, lyrics_api_key)
        context = {'image': True, 'uri': img_uri, 'user_id': user_id}
    return render(request, 'spot-auth/callback.html', context)


def auth(request):
    # scope = "user-top-read"
    scope = "user-library-read playlist-read-private user-read-currently-playing user-read-recently-played user-follow-read user-top-read user-read-email"
    url = "https://accounts.spotify.com/authorize"
    redirect_uri = "http://127.0.0.1:8000/callback/"
    params = {'client_id': client_id, 'scope': scope, 'redirect_uri': redirect_uri}

    return redirect(f"https://accounts.spotify.com/authorize?client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}&response_type=code&state=1234abc&show_dialog=false")


def guest(request):
    context = {'image': True, 'uri': 'guest', 'user_id': 'guest'}
    return render(request, 'spot-auth/callback.html', context)


def vision_api(request):
    pusher_channel = randomword(15)
    pusher_event = randomword(15)
    pusher_key = 'bad6c2484fcdd281f3e8'
    context = {'pusher_channel': pusher_channel,
               'pusher_event': pusher_event, 'pusher_key': pusher_key}
    import io
    import chardet
    import base64
    from PIL import Image, ImageDraw

    file_name = request.FILES['myfile'].file

    user_id = request.POST.get('userid')

    login = request.POST.get('login')

    count = request.POST.get('upload_count')
    try:
        file = base64.b64encode(file_name.getvalue()).decode()
    except:

        file_name.seek(0)
        data = file_name.read()
        file_raw = io.BytesIO(data)
        image = Image.open(file_raw)
        a, b = image.size
        print(a, b, "this is original size")
        r = int(((1000000*b)/a)**(0.5))
        c = int(1000000/r)
        print(c, r, "this is converted")
        image = image.resize((c, r), Image.ANTIALIAS)
        output = io.BytesIO()

        image.save('resized_image.jpg', quality=95)
        with open("resized_image.jpg", "rb") as image_file:
            file = base64.b64encode(image_file.read()).decode()

        print(image.size)

    song_suggestions.delay(file, pusher_channel, pusher_event, user_id, login, count)

    return render(request, 'spot-auth/results.html', context)


def results(request):
    return render(request, 'spot-auth/results.html')


def task(uid):
    pusher_client.trigger(uid, 'my-event', {'message': 'hello world 0'})
    time.sleep(2)
    pusher_client.trigger(uid, 'my-event', {'message': 'hello world 2'})
    time.sleep(2)
    pusher_client.trigger(uid, 'my-event', {'message': 'hello world 4'})
    time.sleep(2)
    pusher_client.trigger(uid, 'my-event', {'message': 'hello world 6'})
    print('6')
    return


def randomword(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def pi(request):

    pusher_channel = randomword(15)
    pusher_event = randomword(15)
    pusher_key = 'bad6c2484fcdd281f3e8'
    pusher_task.delay(pusher_channel, pusher_event)
    context = {'pusher_channel': pusher_channel,
               'pusher_event': pusher_event, 'pusher_key': pusher_key}
    return render(request, 'spot-auth/pusher.html', context)


def test(request):
    return render(request, 'spot-auth/main.html')
