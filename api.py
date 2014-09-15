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
        parser.add_argument('name', type=str, required=True)
        request_params = parser.parse_args()
        response = User.signup(
            email=request_params['email'],
            password=request_params['password'],
            name=request_params['name']
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


class Mail(restful.Resource):

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=int, required=True)
        parser.add_argument('sender_id', type=int, required=True)
        parser.add_argument('message', type=str, required=True)
        parser.add_argument('subject', type=str, required=True)
        request_params = parser.parse_args()

        data = util.mail(request_params['user_id'], request_params['sender_id'], request_params['message'], request_params['subject'])

        return data

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=int, required=True)
        parser.add_argument('seq_no', type=int, required=True)
        request_params = parser.parse_args()

        data = util.subject(request_params['user_id'], request_params['seq_no'])

        return data


class UpdateRead(restful.Resource):

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=int, required=True)
        parser.add_argument('msg_id', type=int, required=True)
        request_params = parser.parse_args()

        data = util.update_read(request_params['user_id'], request_params['msg_id'])

        return data


class Follow(restful.Resource):

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=int, required=True)
        parser.add_argument('band_id', type=int, required=True)
        request_params = parser.parse_args()

        data = util.follow(request_params['user_id'], request_params['band_id'])

        return data


class UsersFollowing(restful.Resource):

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=int, required=True)
        parser.add_argument('band_id', type=int, required=True)
        request_params = parser.parse_args()

        data = util.users_following(request_params['user_id'], request_params['msg_id'])

        return data


class GetSines(restful.Resource):

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('seq_no', type=int, required=True)
        parser.add_argument('band_id', type=int, required=True)
        request_params = parser.parse_args()

        data = util.get_sines(request_params['seq_no'], request_params['band_id'])

        return data


class AddPlayTimes(restful.Resource):

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=int, required=True)
        parser.add_argument('song_id', type=int, required=True)
        request_params = parser.parse_args()

        data = util.users_following(request_params['user_id'], request_params['song_id'])

        return data


class Collaboration(restful.Resource):

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=int, required=True)
        parser.add_argument('sender', type=int, required=True)
        parser.add_argument('message', type=str, required=True)
        parser.add_argument('audio', type=int, required=True)
        request_params = parser.parse_args()

        data = util.collab(request_params['user_id'], request_params['sender'], request_params['message'], request_params['audio'])

        return data


class CollaborationRetrieve(restful.Resource):

    def get(self):
        parser = reqparse.RequestParser()


class CollaborationRequest(restful.Resource):

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=int, required=True)
        parser.add_argument('requested_to', type=int, required=True)
        request_params = parser.parse_args()

        data = util.collab_req(request_params['user_id'], request_params['requested_to'])

        return data


class CollaborationAccept(restful.Resource):

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=int, required=True)
        parser.add_argument('requested_to', type=int, required=True)
        request_params = parser.parse_args()

        data = util.collab_accept(request_params['user_id'], request_params['requested_to'])

        return data


class GetQuestion(restful.Resource):

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('wall_user_id', type=int, required=True)
        parser.add_argument('seq_no', type=int, required=True)
        request_params = parser.parse_args()

        data = util.get_question(request_params['wall_user_id'], request_params['seq_no'])

        return data

class PostQuestion(restful.Resource):

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=int, required=True)
        parser.add_argument('wall_user_id', type=int, required=True)
        parser.add_argument('question', type=str, required=True)
        request_params = parser.parse_args()

        data = util.post_question(user_id=request_params['user_id'], wall_user_id=request_params['wall_user_id'], question=request_params['question'])

        return data


class GetComment(restful.Resource):

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('ques_id', type=int, required=True)
        request_params = parser.parse_args()

        data = util.get_comment(request_params['ques_id'])

        return data


class GetAnswered(restful.Resource):

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('ques_id', type=int, required=True)
        request_params = parser.parse_args()

        data = util.get_answered(request_params['ques_id'])

        return data


class GetUnanswered(restful.Resource):

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('ques_id', type=int, required=True)
        request_params = parser.parse_args()

        data = util.get_unanswered(request_params['ques_id'])

        return data


class PostAnswer(restful.Resource):

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=int, required=True)
        parser.add_argument('answer', type=str, required=True)
        parser.add_argument('ques_id', type=int, required=True)
        request_params = parser.parse_args()
        print request_params
        data = util.post_answer(user_id=request_params['user_id'], answer=request_params['answer'], ques_id=request_params['ques_id'])

        return data


class PostComment(restful.Resource):

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('ques_id', type=int, required=True)
        parser.add_argument('user_id', type=int, required=True)
        parser.add_argument('comment', type=str, required=True)
        request_params = parser.parse_args()

        data = util.post_comment(request_params['ques_id'],request_params['user_id'], request_params['comment'])

        return data


class DeleteAnswer(restful.Resource):

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('ques_id', type=int, required=True)
        request_params = parser.parse_args()

        data = util.delete_answer(request_params['ques_id'])

        return data


class DeleteQuestion(restful.Resource):

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('ques_id', type=int, required=True)
        request_params = parser.parse_args()

        data = util.delete_question(request_params['ques_id'])

        return data


class DeleteComment(restful.Resource):

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('msg_id', type=int, required=True)
        request_params = parser.parse_args()

        data = util.delete_comment(request_params['msg_id'])

        return data


class DeleteInboxMessage(restful.Resource):

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('msg_id', type=int, required=True)
        request_params = parser.parse_args()

        data = util.delete_inbox_message(request_params['msg_id'])

        return data


class Search(restful.Resource):

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('search_term', type=int, required=True)
        parser.add_argument('query_filter', type=str, required=True)
        request_params = parser.parse_args()

        data = util.search(request_params['search_term'], request_params['query_filter'])

        return data


class GetNotification(restful.Resource):

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=int, required=True)
        parser.add_argument('seq_no', type=int, required=True)
        request_params = parser.parse_args()

        data = util.get_notif(request_params['user_id'], request_params['seq_no'])

        return data


class AddFollow(restful.Resource):

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('band_id', type=int, required=True)
        parser.add_argument('user_id', type=int, required=True)
        request_params = parser.parse_args()

        data = util.add_follow(band_id=request_params['band_id'], user_id=request_params['user_id'])

        return data


class TotalFollow(restful.Resource):

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('band_id', type=int, required=True)
        request_params = parser.parse_args()

        data = util.total_follow(band_id=request_params['band_id'])

        return data


class Back(restful.Resource):

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=int, required=True)
        parser.add_argument('camp_id', type=int, required=True)
        parser.add_argument('amount', type=int, required=True)
        request_params = parser.parse_args()

        data = util.back(user_id=request_params['user_id'], camp_id=request_params['camp_id'], amount=request_params['amount'])

        return data

class CheckIfBacker(restful.Resource):

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=int, required=True)
        request_params = parser.parse_args()

        data = util.check_if_backer(user_id=request_params['user_id'])

        return data


class CreateCampaign(restful.Resource):

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=int, required=True)
        parser.add_argument('goal', type=int, required=True)
        parser.add_argument('picture', type=str, required=True)
        parser.add_argument('goal_time', type=str, required=True)
        request_params = parser.parse_args()

        data = util.create_campaign(user_id=request_params['user_id'], goal=request_params['goal'], picture=request_params['picture'], goal_time=request_params['goal_time'])

        return data


class GetUserRunningCampaign(restful.Resource):

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=int, required=True)
        parser.add_argument('seq_no', type=int, required=True)
        request_params = parser.parse_args()

        data = util.get_user_running_campaign(user_id=request_params['user_id'], seq_no=request_params['seq_no'])

        return data

api.add_resource(GetNewTrack, '/get_next_track')
api.add_resource(Signup, '/signup')
api.add_resource(Login, '/login')
api.add_resource(UserSongsData, '/user_songs_data')
api.add_resource(SongVote, '/like_dislike')
api.add_resource(Mail, '/mail')
api.add_resource(UpdateRead, '/update_read')
api.add_resource(Follow, '/follow')
api.add_resource(UsersFollowing, '/users_following')
api.add_resource(GetSines, '/get_sines')
api.add_resource(AddPlayTimes, '/add_play_times')
api.add_resource(Collaboration, '/collab')
api.add_resource(CollaborationRetrieve, '/collab_ret')
api.add_resource(CollaborationRequest, '/collab_req')
api.add_resource(CollaborationAccept, '/collab_accept')
api.add_resource(GetQuestion, '/get_question')
api.add_resource(PostQuestion, '/post_question')
api.add_resource(GetComment, '/get_comment')
api.add_resource(GetAnswered, '/get_answered')
api.add_resource(GetUnanswered, '/get_unanswered')
api.add_resource(PostAnswer, '/post_answer')
api.add_resource(PostComment, '/post_comment')
api.add_resource(DeleteAnswer, '/delete_answer')
api.add_resource(DeleteQuestion, '/delete_question')
api.add_resource(DeleteComment, '/delete_comment')
api.add_resource(DeleteInboxMessage, '/delete_inbox_message')
api.add_resource(Search, '/search')
api.add_resource(GetNotification, '/get_notif')
api.add_resource(AddFollow, '/add_follow')
api.add_resource(TotalFollow, '/total_follow')
api.add_resource(Back, '/back')
api.add_resource(CheckIfBacker, '/check_if_backer')
api.add_resource(CreateCampaign, '/create_campaign')
api.add_resource(GetUserRunningCampaign, '/get_user_running_campaign')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True, use_reloader=True)

