import warnings
import string
import pandas as pd
import numpy as np
import nltk
from nltk.corpus import stopwords
import pickle
import gensim
import tensorflow as tf

warnings.filterwarnings("ignore", category=DeprecationWarning)

loaded_model = tf.keras.models.load_model('SentimentAnalysis/PleaseWork.h5')
print("DL Model loaded from disk.")
with open('SentimentAnalysis/tokenizer.pickle', 'rb') as handle:
    tokenizer = pickle.load(handle)
print('Loaded Tokenizer from disk.')
w2v_API = pickle.load(open('SentimentAnalysis/w2v_API.sav', 'rb'))
print('Loaded Word2Vec model.')


def clean_data(filename):

    df = pd.read_csv(filename)
    print('Reading file: ', filename)

    df = df[df['Song_Lyrics'].notnull()]
    df = df[df['Song_lyrics'].str.split().str.len() > 100]
    df['Song_lyrics'] = df['Song_lyrics'].replace('\n', ' ', regex=True)
    df['clean_lyrics'] = df['Song_lyrics'].apply(
        lambda s: s.translate(str.maketrans('', '', string.punctuation)))
    df['clean_lyrics'] = df['clean_lyrics'].str.lower()

    new_filename = filename[:-4] + '_modified.csv'
    df.to_csv(new_filename, index=False)
    print('Cleaned user tracks, created modified file')

    return new_filename


def sentence_vectorizer2(sentence):

    words = sentence.split()
    mean = np.mean([ft_model[word]
                    for word in words if word in ft_model.wv.vocab] or [np.zeros(50,)], axis=0)
    return mean


def label_user(filename, user_id):

    print('Reading file: ', filename)
    test_data = pd.read_csv(filename)
    X = tokenizer.texts_to_sequences(test_data['clean_lyrics'].values)
    MAX_SEQ_LEN = 300
    X = tf.keras.preprocessing.sequence.pad_sequences(
        X, maxlen=MAX_SEQ_LEN, padding='post', truncating='pre')
    batch_size = 16
    pred = loaded_model.predict_classes(X, batch_size=batch_size, verbose=1)
    prob = loaded_model.predict(X, batch_size=batch_size, verbose=1)
    pred_prob = np.max(prob, axis=1)
    labels_user = []
    for i in range(len(pred)):
        if pred[i] == 0:
            labels_user.append('happy')
        elif pred[i] == 1:
            labels_user.append('party')
        if pred[i] == 2:
            labels_user.append('relax')
        if pred[i] == 3:
            labels_user.append('sad')
    column_names = ['SID', 'Artist', 'Song_Name', 'Labels', 'Probability']
    df = pd.DataFrame(list(zip(test_data.SID, test_data.Artist, test_data.Song_Name,
                               labels_user, pred_prob)), columns=column_names)
    new_filename = 'Documents/' + user_id + '_labels.csv'
    df.to_csv(new_filename, index=False)
    print('Created user labels file')

    return


def label_top50(filename):

    print('Reading file: ', filename)
    test_data = pd.read_csv(filename)
    X = tokenizer.texts_to_sequences(test_data['clean_lyrics'].values)
    MAX_SEQ_LEN = 300
    X = tf.keras.preprocessing.sequence.pad_sequences(
        X, maxlen=MAX_SEQ_LEN, padding='post', truncating='pre')
    batch_size = 16
    pred = loaded_model.predict_classes(X, batch_size=batch_size, verbose=1)
    prob = loaded_model.predict(X, batch_size=batch_size, verbose=1)
    pred_prob = np.max(prob, axis=1)
    labels_user = []
    for i in range(len(pred)):
        if pred[i] == 0:
            labels_user.append('happy')
        elif pred[i] == 1:
            labels_user.append('party')
        if pred[i] == 2:
            labels_user.append('relax')
        if pred[i] == 3:
            labels_user.append('sad')

    column_names = ['SID', 'Artist', 'Song_Name', 'Labels', 'Probability']
    df = pd.DataFrame(list(zip(test_data.SID, test_data.Artist, test_data.Song_Name, labels_user,
                               pred_prob)), columns=column_names)
    new_filename = 'Documents/' + filename[:-13] + '_labels.csv'
    df.to_csv(new_filename, index=False)
    print('Created Top 50 songs labels file')

    return


def output_songs(listoflines, login, user_id=0, num=1):

    lines = [line.split() for line in listoflines]
    listofwords = [word for sublist in lines for word in sublist]
    listofwords_filtered = [word for word in listofwords if word not in stopwords.words('english')]
    listofwords_filtered = [word.lower() for word in listofwords_filtered]
    api_word = np.mean([w2v_API[word] for word in listofwords_filtered if word in w2v_API.wv.vocab] or [
        np.zeros(300,)], axis=0)

    api_classes = w2v_API.distances(api_word, other_words=('happy', 'sad', 'relax', 'party'))
    tags = ['happy', 'sad', 'relax', 'party']
    index = np.argmax(api_classes)
    api_label = tags[index]

    filename2 = ""
    if num == 1:
        filename2 = 'Documents/1_labels.csv'
    elif num == 2:
        filename2 = 'Documents/2_labels.csv'
    elif num == 3:
        filename2 = 'Documents/3_labels.csv'
    elif num == 4:
        filename2 = 'Documents/4_labels.csv'
    elif num == 5:
        filename2 = 'Documents/5_labels.csv'

    if login == 'true':
        print('User has logged in.')
        filename = 'Documents/' + user_id + '_labels.csv'
        df_user = pd.read_csv(filename)
        output_songs1 = df_user[df_user['Labels'] == api_label]
        output_songs1 = output_songs1.sort_values(['Probability'], ascending=False)
        df_top50 = pd.read_csv(filename2)
        output_songs2 = df_top50[df_top50['Labels'] == api_label]
        output_songs2 = output_songs2.sort_values(['Probability'], ascending=False)
        output_songs = pd.concat([output_songs1[:3], output_songs2[:2]])
        ids = list(output_songs['SID'])[:5]
        ids = [id[8:] for id in ids]
        print(output_songs)
    else:
        print('User has not logged in.')
        df_top50 = pd.read_csv(filename2)
        output_songs = df_top50[df_top50['Labels'] == api_label]
        output_songs = output_songs.sort_values(['Probability'], ascending=False)
        output_songs = output_songs[:5]
        ids = list(output_songs['SID'])[:5]
        ids = [id[8:] for id in ids]
        print(output_songs)

    print('Created the ids')
    return ids


def write_tracks(tracks, user_id, key):
    import requests
    rows_list = []
    f = open("tracks.txt", "w+")
    for i, item in enumerate(tracks['items']):
        track = item['track']
        spot_id = track['uri']
        t_name = track['name']
        t_artist = track['artists'][0]['name']
        f.write(str(i) + ') Artist: ' + t_artist + "  " + 'Song: ' + t_name + "\n")
        params = {'apikey': key, 'q_track': t_name, 'q_artist': t_artist}
        url1 = 'http://api.musixmatch.com/ws/1.1/track.search'
        res1 = requests.get(url=url1, params=params)
        data1 = res1.json()
        print(data1, "data1 \n")
        try:
            t_id = data1['message']['body']['track_list'][0]['track']['track_id']
            url2 = 'http://api.musixmatch.com/ws/1.1/track.lyrics.get'
            p = {'apikey': key, 'track_id': t_id}
            res2 = requests.get(url=url2, params=p)
            data2 = res2.json()
            print(data2, "data2 \n")
            lyr = data2['message']['body']['lyrics']['lyrics_body']
            f.write(lyr + '\n')
            row = [spot_id, t_name, t_artist, lyr]
            rows_list.append(row)
        except Exception as e:
            print('some error with ' + t_name)
            print(e)

    f.close()
    column_names = ['SID', 'Song_Name', 'Artist', 'Song_lyrics']
    df = pd.DataFrame(rows_list, columns=column_names)
    filename = 'Documents/' + user_id + '.csv'
    df.to_csv(filename, index=False)
    print('Created User tracks file')

    return filename


def visionapi(content, login, user_id, count):
    import requests
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
    labels = result['responses'][0]['labelAnnotations']
    data = []
    for item in labels:
        data.append(item['description'])
    print(data)
    ids = output_songs(data, login, user_id, count)

    return ids
