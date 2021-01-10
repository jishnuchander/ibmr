from __future__ import absolute_import, unicode_literals
from celery import shared_task
import pusher
import time
import json
from SentimentAnalysis import Sentiment_Analysis as sa
from spot_auth.models import Profile


class LogPusher(object):
    def __init__(self, channel, event):

        self.pusher_client = pusher.Pusher(
            app_id='app_id',
            key='key',
            secret='secret',
            cluster='cluster',
            ssl=True
        )
        self.event = event
        self.channel = channel

    def send(self, data):
        self.pusher_client.trigger(self.channel, self.event, json.dumps(data))


@shared_task
def pusher_task(pusher_channel, pusher_event):

    log_pusher = LogPusher(pusher_channel, pusher_event)
    print("task started")
    time.sleep(10)
    log_pusher.send({'status': 'working'})
    return


@shared_task
def lyrics(user_name, user_id, img_uri, playlist, key):
    user_id = str(1)
    user_csv = sa.write_tracks(playlist, user_id, key)
    cleaned_csv = sa.clean_data(user_csv)
    # sa.label_user(cleaned_csv,user_id)
    sa.label_top50(cleaned_csv)
    flag = Profile.objects.filter(user_id="user_id")
    # print(flag,"flag")
    if not flag:
        profile = Profile(
            username=user_name,
            user_id=user_id,
            image_uri=img_uri,
            playlist=cleaned_csv
        )
        profile.save()
    return


def api(content):
    import base64
    import requests
    import json
    print("inside api")
    URL = "https://vision.googleapis.com/v1/images:annotate?key=key"
    data = {
        "requests": [
            {
                "image": {
                    "content": content
                },
                "features": [
                    {
                        "type": "LABEL_DETECTION",  # other options: LABEL_DETECTION FACE_DETECTION LOGO_DETECTION CROP_HINTS WEB_DETECTION
                        "maxResults": 10
                    }
                ]
            }
        ]
    }
    r = requests.post(URL, json=data)
    result = r.json()
    print(result)
    labels = result['responses'][0]['labelAnnotations']
    data = []
    for item in labels:
        data.append(item['description'])

    return


@shared_task
def song_suggestions(content, pusher_channel, pusher_event, user_id, login, count):
    import time
    import base64
    import json

    log_pusher = LogPusher(pusher_channel, pusher_event)
    ids = sa.visionapi(content, login, user_id, count)

    f_ids = []
    for i in ids:
        a = i.split(':')
        b = a[0]+'/'+a[1]
        f_ids.append(b)
    log_pusher.send({'ids': f_ids})

    return
