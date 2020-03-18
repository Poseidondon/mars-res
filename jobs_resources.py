from flask_restful import reqparse, abort, Resource
from flask import jsonify

from data import db_session
from data.__all_models import *


PARSER = reqparse.RequestParser()
PARSER.add_argument('team_leader', required=True, type=int)
PARSER.add_argument('job', required=True)
PARSER.add_argument('work_size', required=True, type=int)
PARSER.add_argument('start_date', required=True)
PARSER.add_argument('end_date', required=True)
PARSER.add_argument('collaborators', required=True)
PARSER.add_argument('is_finished', required=True, type=bool)


def abort_if_job_not_found(job_id):
    session = db_session.create_session()
    job = session.query(Jobs).get(job_id)
    if not job:
        abort(404, message=f"Job {job_id} not found")


class JobsResource(Resource):
    def get(self, job_id):
        abort_if_job_not_found(job_id)
        session = db_session.create_session()
        job = session.query(Jobs).get(job_id)
        return jsonify({'job': job.to_dict(
            only=('id', 'team_leader', 'job', 'start_date', 'end_date', 'work_size', 'collaborators', 'is_finished'))})

    def delete(self, job_id):
        abort_if_job_not_found(job_id)
        session = db_session.create_session()
        job = session.query(Jobs).get(job_id)
        session.delete(job)
        session.commit()
        return jsonify({'success': 'OK'})


class JobsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        jobs = session.query(Jobs).all()
        return jsonify({'job': [item.to_dict(
            only=('id', 'team_leader', 'job', 'start_date', 'end_date',
                  'work_size', 'collaborators', 'is_finished')) for item in jobs]})

    def post(self):
        args = PARSER.parse_args()
        session = db_session.create_session()
        job = Jobs(
            team_leader=args['team_leader'],
            job=args['job'],
            work_size=args['work_size'],
            start_date=args['start_date'],
            end_date=args['end_date'],
            collaborators=args['collaborators'],
            is_finished=args['is_finished']
        )
        session.add(job)
        session.commit()
        return jsonify({'success': 'OK'})
