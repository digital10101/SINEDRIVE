__author__ = 'karan'
from flask import Flask, request, redirect, make_response
from flask.ext import restful
from flask.ext.restful import reqparse
from users import User
import hashlib
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
        if flag:
            return {'user_id': user['id'], 'name': user['name'], 'access_type': user['access_type'], 'email': user['email'], 'error': 0}
        else:
            return {'error': user['error']}


api.add_resource(Signup, '/signup')
api.add_resource(Login, '/login')