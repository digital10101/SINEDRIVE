__author__ = 'karan'
from flask import Flask, request, redirect, make_response
from flask.ext import restful
from flask.ext.restful import reqparse
from users import User
import hashlib
import util

app = Flask(__name__)
api = restful.Api(app)


@app.before_request
def remove_trailing_slash():
    if request.path != '/' and request.path.endswith('/'):
        return redirect(request.path[:-1])


class Signup(restful.Resource):

    def post(self):

        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        request_params = parser.parse_args()
        response = User.signup(
            request_params['email'],
            request_params['password']
        )
        return response


class Login(restful.Resource):

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        request_params = parser.parse_args()
        flag, user = User.authenticate_email(request_params['username'], hashlib.md5(request_params['password']).hexdigest())
        return user


class UserSongsData(restful.Resource):

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=int, required=True)
        parser.add_argument('seg_no', type=int, required=True)

        request_params = parser.parse_args()

        data = util.get_user_song_data(request_params['user_id'], request_params['seg_no'])

        return data


class GetNewTrack(restful.Resource):

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=int, required=True)
        request_params = parser.parse_args()

        data = util.get_next_track(request_params['user_id'])

        return data


class SongVote(restful.Resource):

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=int, required=True)
        parser.add_argument('song_id', type=int, required=True)
        parser.add_argument('liked', type=int, required=True)
        parser.add_argument('disliked', type=int, required=True)
        request_params = parser.parse_args()

        data = util.song_vote(request_params['user_id'], request_params['song_id'], request_params['liked'], request_params['disliked'])

        return data

api.add_resource(GetNewTrack, '/get_next_track')
api.add_resource(Signup, '/signup')
api.add_resource(Login, '/login')
api.add_resource(UserSongsData, '/user_songs_data')
api.add_resource(SongVote, '/like_dislike')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True, use_reloader=True)

