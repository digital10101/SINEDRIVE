__author__ = 'karan'
from mysql_wrapper import Mysql
from operator import itemgetter
import random


def get_user_song_data(user_id, offset):

    songs = songs_g_values(offset)
    songs_rel = get_songs_related_to(user_id)

    song_g_ids = list()
    for song in songs:
        song_g_ids.append(song['song_id'])

    song_rel_ids = list()
    for song in songs_rel:
        song_rel_ids.append(song['song_id'])

    songs_g = dict()
    songs_r = dict()

    for song in songs:
        songs_g[song['song_id']] = song
    for song in songs_rel:
        songs_r[song['song_id']] = song

    for id_g in song_g_ids:
        songs_g[id_g]['liked'] = 0
        songs_g[id_g]['disliked'] = 0

    for id_g in song_g_ids:
        for id_r in song_rel_ids:
            if id_g == id_r:
                songs_g[id_g]['liked'] = songs_r[id_g]['liked']
                songs_g[id_g]['disliked'] = songs_r[id_g]['disliked']

    return {'error': 0, 'data': songs_g}


def songs_g_values(offset):
    query = 'Select song_filename, album, song_id, title, band_name from songs_info order by g_value desc limit 20 offset %s' % str((offset - 1) * 20)
    mysql = Mysql()
    rows = ()
    try:
        rows = mysql.getManyRows(query)
    except Exception as e:
        print e
    mysql.close()
    print rows
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

def get_next_likes(user_id, song_id):

    query = 'Select liked, disliked from user_songs where user_id = %d and song_id = %d' % (user_id, song_id)

    mysql = Mysql()
    row = None
    try:
        row = mysql.getSingleRow(query)
    except Exception as e:
        print e
    mysql.close()
    return row


def get_next_track(user_id):

    query = 'SELECT song_filename, album, song_id, title, band_name FROM songs_info ORDER BY RAND() LIMIT 1'

    mysql = Mysql()
    row = {}
    try:
        row = mysql.getSingleRow(query)
    except Exception as e:
        print e
    mysql.close()
    next_like = get_next_likes(user_id, row['song_id'])

    row['liked'] = next_like['liked'] if next_like else 0
    row['disliked'] = next_like['disliked'] if next_like else 0
    response = {
        'data': row,
        'error': 0
    }
    return response


def song_vote(user_id, song_id, liked, disliked):

    query = 'insert into `user_songs` (user_id, song_id, played_times, liked, disliked) values (%d, %d, 0, %d, %d) on duplicate key update liked = %d, disliked = %d' % (user_id, song_id, liked, disliked, liked, disliked)
    mysql = Mysql()
    try:
        mysql.execute(query)
    except Exception as e:
        print e
    mysql.close()

    query = 'select sum(liked) as numl, sum(disliked) as numd, sum(played_times) as numpt from user_songs where song_id = %d' % song_id
    row = None
    try:
        row = mysql.getSingleRow(query)
    except Exception as e:
        print e
    mysql.close()

    g_value = (row['numl'] - row['numd']) * 2 + row['numpt']
    query = 'update songs_info set g_value = %d where song_id = %d' %(g_value, song_id)
    mysql = Mysql()
    try:
        mysql.execute(query)
    except Exception as e:
        print e
    mysql.close()
    return {'error': 0}


