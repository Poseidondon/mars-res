from flask_restful import reqparse, abort, Resource
from flask import jsonify

from data import db_session
from data.__all_models import *


PARSER = reqparse.RequestParser()
PARSER.add_argument('surname', required=True)
PARSER.add_argument('name', required=True)
PARSER.add_argument('age', required=True, type=int)
PARSER.add_argument('position', required=True)
PARSER.add_argument('speciality', required=True)
PARSER.add_argument('address', required=True)
PARSER.add_argument('email', required=True)
PARSER.add_argument('speciality', required=True)
PARSER.add_argument('password', required=True)


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f"User {user_id} not found")


class UserResource(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        return jsonify({'user': user.to_dict(
            only=('id', 'surname', 'name', 'age', 'position', 'speciality', 'address', 'email', 'modified_date'))})

    def delete(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})


class UsersListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify({'user': [item.to_dict(
            only=('id', 'surname', 'name', 'age', 'position', 'speciality',
                  'address', 'email', 'modified_date')) for item in users]})

    def post(self):
        args = PARSER.parse_args()
        session = db_session.create_session()
        user = User(
            surname=args['surname'],
            name=args['name'],
            age=args['age'],
            position=args['position'],
            speciality=args['speciality'],
            address=args['address'],
            email=args['email']
        )
        user.set_password(args['password'])
        session.add(user)
        session.commit()
        return jsonify({'success': 'OK'})
