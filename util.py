__author__ = 'karan'
from mysql_wrapper import Mysql
import MySQLdb
from operator import itemgetter
import random
import ujson


def get_user_song_data(user_id, offset, genre):

    songs = songs_g_values(offset, genre)
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


def songs_g_values(offset, genre):
    query = 'Select song_filename, album, song_id, title, band_name from songs_info order by g_value desc limit 20 offset %s' % str((offset - 1) * 20)
    query1 = 'Select song_filename, album, song_id, title, band_name from songs_info where genre = %s order by g_value desc limit 20 offset %s' % (genre, str((offset - 1) * 20))
    if genre == 'show all':
        mysql = Mysql()
        rows = ()
        try:
            rows = mysql.getManyRows(query)
        except Exception as e:
            print e
        mysql.close()
        print rows
    else:
        mysql = Mysql()
        rows = ()
        try:
            rows = mysql.getManyRows(query1)
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
    query = 'update songs_info set g_value = %d where song_id = %d'
    mysql = Mysql()
    try:
        mysql.execute(query, (g_value, song_id))
    except Exception as e:
        print e
    mysql.close()
    return {'error': 0}


def mail(rec_id, sender_id, message, sub):
    mysql = Mysql()
    query = 'insert into `inbox` (rec_id, sender_id, message, subject) values(%d, %d, "%s", "%s")'
    try:
        mysql.execute(query, (rec_id, sender_id, mysql.escape_string(message), mysql.escape_string(sub)))
    except Exception as e:
        print e
    mysql.close()

    msg_query = 'select msg_id from inbox where rec_id = %d and sender_id = %d and message = "%s" and subject = "%s"' % (rec_id, sender_id, mysql.escape_string(message), mysql.escape_string(sub))
    rows = {}
    mysql = Mysql()
    try:
        rows = mysql.getSingleRow(msg_query)
    except Exception as e:
        print e
    mysql.close()
    msg_id = rows['msg_id']

    query = 'insert into `notification` (type_id, msg_id, created_by, for_id, viewed) values (102, %d, %d, %d, 0)'
    mysql = Mysql()
    try:
        mysql.execute(query, (msg_id, sender_id, rec_id))
    except Exception as e:
        print e
    mysql.close()
    return {'error': 0}


def subject(rec_id, seq_no):

    query = 'Select login.name , inbox.msg_id , inbox.subject , inbox.read , inbox.timestamp from inbox join login on inbox.sender_id = login.user_id where inbox.rec_id = %d order by inbox.timestamp desc limit 10 offset %s' % (rec_id, str((seq_no - 1) * 10))
    mysql = Mysql()
    rows = None
    try:
        rows = mysql.getManyRows(query)
    except Exception as e:
        print e
    mysql.close()
    rows = list(rows)
    msg_dict = dict()
    for row in rows:
        row['timestamp'] = row['timestamp'].isoformat()
        msg_dict[str(row['msg_id'])] = row

    response = {
        'data': msg_dict,
        'error': 0
    }

    return response


def update_read(msg_id):

    query = 'update inbox set read = 1 where msg_id = %d' % msg_id
    mysql = Mysql()
    try:
        mysql.execute(query)
    except Exception as e:
        print e
    mysql.close()
    return {'error': 0}


def follow(band_id):

    query = 'select count(user_id) from follow_data where band_id = %d' % band_id
    mysql = Mysql()
    row = {}
    try:
        row = mysql.getSingleRow(query)
    except Exception as e:
        print e
    mysql.close()
    return row


def users_following(user_id, band_id):

    query = 'insert into `follow_data` (user_id, band_id) values(%d, %d)' % (user_id, band_id)
    mysql = Mysql()
    try:
        mysql.execute(query)
    except Exception as e:
        print e
    mysql.close()
    return {'error': 0}


def get_sines(seq_no, band_id):

    query = 'select * from songs_info where band_id = %d order by Timestamp desc limit 10 offset %s' % (band_id, str((seq_no - 1) * 10))
    mysql = Mysql()
    rows = None
    try:
        rows = mysql.getManyRows(query)
    except Exception as e:
        print e
    mysql.close()
    rows = list(rows)
    msg_dict = dict()
    for row in rows:
        row['timestamp'] = row['timestamp'].isoformat()
        msg_dict[str(row['msg_id'])] = row

    response = {
        'data': msg_dict,
        'error': 0
    }

    return response


def add_played_times(user_id, song_id):

    query = 'insert into `user_songs` (played_times) values (0) on duplicate key update played_times = (played_times + 1) where user_id = %d and song_id = %d' % (user_id, song_id)
    mysql = Mysql()
    try:
        mysql.execute(query)
    except Exception as e:
        print e
    mysql.close()
    return {'error': 0}


def collab(user_id, sender, message, audio):

    query = 'insert into collab_info (user_id, sender, message, audio) values (%d, %d, "%s", %d)'
    mysql = Mysql()
    try:
        mysql.execute(query, (user_id, sender, message, audio))
    except Exception as e:
        print e
    mysql.close()

    msg_query = 'select msg_id from collab_info where user_id = %d and sender = %d and message = "%s" and audio = %d' % (user_id, sender, mysql.escape_string(message), audio)
    rows = {}
    mysql = Mysql()
    try:
        rows = mysql.getSingleRow(msg_query)
    except Exception as e:
        print e
    mysql.close()
    msg_id = rows['msg_id']

    query = 'insert into `notification` (type_id, msg_id, created_by, for_id, viewed) values (101, %d, %d, %d, 0)'
    mysql = Mysql()
    try:
        mysql.execute(query, (msg_id, sender, user_id))
    except Exception as e:
        print e
    mysql.close()

    return {'error': 0}


def collab_req(user_id, requested_to):

    query = 'insert into `collab_request` (user_id, requested_to) values (%d, %d)' % (user_id, requested_to)
    mysql = Mysql()
    try:
        mysql.execute(query)
    except Exception as e:
        print e
    mysql.close()
    return {'error': 0}


def collab_accept(user_id, requested_to):

    query = 'update collab_request set accepted = 1 where user_id = %d and requested_to = %d' % (user_id, requested_to)
    mysql = Mysql()
    try:
        mysql.execute(query)
    except Exception as e:
        print e
    mysql.close()
    return {'error': 0}


def get_question(wall_user_id, seq_no):

    query = 'select * from questions where wall_user_id = %d order by Timestamp desc limit 10 offset %s' % (wall_user_id, str((seq_no - 1) * 10))
    mysql = Mysql()
    rows = None
    try:
        rows = mysql.getManyRows(query)
    except Exception as e:
        print e
    mysql.close()
    rows = list(rows)
    ques_dict = dict()
    for row in rows:
        row['timestamp'] = row['timestamp'].isoformat()
        ques_dict[str(row['ques_id'])] = row

    response = {
        'data': ques_dict,
        'error': 0
    }

    # query1 = 'update questions set read = 1 where wall_user_id = %d' % wall_user_id
    # mysql = Mysql()
    # try:
    #     mysql.execute(query1)
    # except Exception as e:
    #     print e
    # mysql.close()

    return response


def post_question(question, user_id, wall_user_id):

    query = 'insert into `questions` (question, user_id, wall_user_id) values (%s, %d, %d)' % (question, user_id, wall_user_id)
    mysql = Mysql()
    try:
        mysql.execute(query)
    except Exception as e:
        print e
    mysql.close()

    msg_query = 'select ques_id from questions where question = "%s" and user_id = %d and wall_user_id = %d' % (question, user_id, wall_user_id)
    rows = {}
    mysql = Mysql()
    try:
        rows = mysql.getSingleRow(msg_query)
    except Exception as e:
        print e
    mysql.close()
    msg_id = rows['ques_id']

    query = 'insert into `notification` (type_id, msg_id, created_by, for_id, viewed) values (103, %d, %d, %d, 0)'
    mysql = Mysql()
    try:
        mysql.execute(query, (msg_id, user_id, wall_user_id))
    except Exception as e:
        print e
    mysql.close()

    return {'error': 0}


def get_comment(user_id):

    query = 'select * from comments where user_id = %d' % user_id
    mysql = Mysql()
    rows = None
    try:
        rows = mysql.getManyRows(query)
    except Exception as e:
        print e
    mysql.close()
    rows = list(rows)
    comment_dict = dict()
    for row in rows:
        row['timestamp'] = row['timestamp'].isoformat()
        comment_dict[str(row['msg_id'])] = row

    response = {
        'data': comment_dict,
        'error': 0
    }

    return response


def get_answered(ques_id):

    query = 'select ques_id, question, user_id, wall_user_id, timestamp from questions where ques_id = %d and answer_flag = 1' % ques_id
    mysql = Mysql()
    rows = None
    try:
        rows = mysql.getManyRows(query)
    except Exception as e:
        print e
    mysql.close()
    rows = list(rows)
    ans_dict = dict()
    for row in rows:
        row['timestamp'] = row['timestamp'].isoformat()
        ans_dict[str(row['ques_id'])] = row

    response = {
        'data': ans_dict,
        'error': 0
    }

    return response


def get_unanswered(ques_id):

    query = 'select ques_id, question, user_id, wall_user_id, timestamp from questions where ques_id = %d and answer_flag = 0' % ques_id
    mysql = Mysql()
    rows = None
    try:
        rows = mysql.getManyRows(query)
    except Exception as e:
        print e
    mysql.close()
    rows = list(rows)
    unans_dict = dict()
    for row in rows:
        row['timestamp'] = row['timestamp'].isoformat()
        unans_dict[str(row['ques_id'])] = row

    response = {
        'data': unans_dict,
        'error': 0
    }

    return response


def post_answer(user_id, answer):

    query = 'update questions set answer_flag = 1 and answer = %s were user_id = %d' % (answer, user_id)
    mysql = Mysql()
    try:
        mysql.execute(query)
    except Exception as e:
        print e
    mysql.close()

    msg_query = 'select ques_id, wall_user_id from questions where answer = "%s" and user_id = %d' % (answer, user_id)
    rows = {}
    mysql = Mysql()
    try:
        rows = mysql.getSingleRow(msg_query)
    except Exception as e:
        print e
    mysql.close()
    msg_id = rows['ques_id']
    wall_id = rows['wall_user_id']

    query = 'insert into `notification` (type_id, msg_id, created_by, for_id, viewed) values (104, %d, %d, %d, 0)'
    mysql = Mysql()
    try:
        mysql.execute(query, (msg_id, wall_id, user_id))
    except Exception as e:
        print e
    mysql.close()

    return {'error': 0}


def post_comment(ques_id, user_id, comment):

    query = 'update comments set user_id = case when ques_id = %d then %d else user_id end, comment = case when ques_id = %d then %s else comment end' % (ques_id, user_id, ques_id, comment)
    mysql = Mysql()
    try:
        mysql.execute(query)
    except Exception as e:
        print e
    mysql.close()
    return {'error': 0}


def delete_answer(ques_id):

    query = 'update questions set answer = null, answer_flag = 0 where ques_id = %d' % ques_id
    mysql = Mysql()
    try:
        mysql.execute(query)
    except Exception as e:
        print e
    mysql.close()
    return {'error': 0}


def delete_question(ques_id):

    query = 'delete from question where ques_id = %d' % ques_id
    mysql = Mysql()
    try:
        mysql.execute(query)
    except Exception as e:
        print e
    mysql.close()

    query = 'delete from comments where ques_id = %d' % ques_id
    mysql = Mysql()
    try:
        mysql.execute(query)
    except Exception as e:
        print e
    mysql.close()

    return {'error': 0}


def delete_comment(msg_id):

    query = 'delete from comments where msg_id = %d' % msg_id
    mysql = Mysql()
    try:
        mysql.execute(query)
    except Exception as e:
        print e
    mysql.close()
    return {'error': 0}


def delete_inbox_message(msg_id):

    query = 'delete from inbox where msg_id = %d' % msg_id
    mysql = Mysql()
    try:
        mysql.execute(query)
    except Exception as e:
        print e
    mysql.close()
    return {'error': 0}


count = 0
final_result = list()


def srch_song(term):

    global final_result
    global count

    query = 'select * from songs_info where title like %%%d%% LIMIT 15'
    rows = None
    mysql = Mysql()
    try:
        rows = mysql.getManyRows(query, term)
    except Exception as e:
        print e
    mysql.close()
    if len(query) > 0:
        final_result.append(rows)
        return len(rows)
    else:
        return 0


def srch_album(term):

    global final_result
    global count

    query = 'select album_filename, album, band_name, band_id , count(album)from songs_info where album like %%%d%% group by album LIMIT 15'
    rows = None
    mysql = Mysql()
    try:
        rows = mysql.getManyRows(query, term)
    except Exception as e:
        print e
    mysql.close()
    if len(query) > 0:
        final_result.append(rows)
        return len(rows)
    else:
        return 0


def srch_artist(term):

    global final_result
    global count

    query = 'select band_name, band_id, login.profile_pic from songs_info join login on login.user_id = songs_info.band_id where album like %%%d%% LIMIT 15'
    rows = None
    mysql = Mysql()
    try:
        rows = mysql.getManyRows(query, term)
    except Exception as e:
        print e
    mysql.close()
    if len(query) > 0:
        final_result.append(rows)
        return len(rows)
    else:
        return 0


def srch_person(term):

    global final_result
    global count

    query = 'select band_name, band_id, login.profile_pic from songs_info join login on login.user_id = songs_info.band_id where album like %%%d%% LIMIT 15'
    rows = None
    mysql = Mysql()
    try:
        rows = mysql.getManyRows(query, term)
    except Exception as e:
        print e
    mysql.close()
    if len(query) > 0:
        final_result.append(rows)
        return len(rows)
    else:
        return 0


def search(search_term, query_filter):

    terms = search_term.split(' ')
    search_len = 15
    limit = min(search_len, len(terms))
    global count
    global final_result
    final_result = 0

    if query_filter == 'all':
        for term in terms[:(limit - 1)]:
            songs = srch_song(term)
            count += songs
            if count < 15:
                album = srch_album(term)
                count += album
                if count < 15:
                    artist = srch_artist(term)
                    count += artist
    elif query_filter == 'song':
        for term in terms[:(limit - 1)]:
            songs = srch_song(term)
            count += songs
    elif query_filter == 'album':
        for term in terms[:(limit - 1)]:
            album = srch_album(term)
            count += album
    elif query_filter == 'artist':
        for term in terms[:(limit - 1)]:
            artist = srch_artist(term)
            count += artist

    return final_result


def get_notif(user_id, seq_no):

    query = 'select * from notification where viewed = 0 and for_id = %d order by Timestamp desc limit 15 offset %s'
    mysql = Mysql()
    rows = None
    try:
        rows = mysql.getManyRows(query, (user_id, str((seq_no - 1) * 10)))
    except Exception as e:
        print e
    mysql.close()

    query = 'update notification set viewed = 1 where viewed = 0 and for_id = %d'
    mysql = Mysql()
    try:
        mysql.execute(query, user_id)
    except Exception as e:
        print e
    mysql.close()

    return rows

