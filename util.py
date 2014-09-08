__author__ = 'karan'
from mysql_wrapper import Mysql
from operator import itemgetter
import random


def get_user_song_data(user_id):

    songs = songs_g_values()
    songs_rel = get_songs_related_to(user_id)

    song_g_ids = list()
    for song in songs:
        song_g_ids.append(song['song_id'])

    song_rel_ids = list()
    for song in songs_rel:
        song_rel_ids.append(song['song_id'])


    if len(songs) > 0:
        songs = sorted(songs, key=lambda k: k['gvalue'])

    return {'error': 0, 'data': songs}


def songs_g_values():
    query = 'Select song_filename, album, song_id, title, band_name from songs_info order by gvalue desc limit 20'
    mysql = Mysql()
    rows = None
    try:
        rows = mysql.getManyRows(query)
    except Exception as e:
        print e
    mysql.close()
    return list(rows)


def get_songs_related_to(user_id):

    query = 'Select song_id, liked, disliked from user_songs where user_id = %d' % user_id
    mysql = Mysql()
    rows = ()
    try:
        rows = mysql.getManyRows(query)
    except Exception as e:
        print e
    mysql.close()
    rows = list(rows)
    return rows


def get_song_data(song_dict_list):

    song_ids = list()
    for song_dict in song_dict_list:
        song_ids.append(song_dict['song_id'])
    query = 'Select song_id, album_filename as album , song_filename as ' \
            'song, gvalue from songs_info where `song_id` in (%s)' % ','.join(map(str, song_ids))

    mysql = Mysql()
    try:
        rows = mysql.getManyRows(query)
    except Exception as e:
        print e
    mysql.close()

    rows = list(rows)

    song_data = sorted(rows, key=itemgetter('gvalue'), reverse=True)

    print song_data



