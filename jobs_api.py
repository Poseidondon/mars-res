import flask
from flask import jsonify, Flask, request

from data import db_session
from data.__all_models import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


blueprint = flask.Blueprint('jobs_api', __name__,
                            template_folder='templates')


@blueprint.route('/api/jobs')
def get_jobs():
    session = db_session.create_session()
    jobs = session.query(Jobs).all()
    return jsonify(
        {
            'jobs':
                [item.to_dict(only=('id', 'job', 'team_leader', 'is_finished'))
                 for item in jobs]
        }
    )


@blueprint.route('/api/jobs/<int:job_id>',  methods=['GET'])
def get_one_news(job_id):
    session = db_session.create_session()
    job = session.query(Jobs).get(job_id)
    if not job:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'job': job.to_dict(only=('id', 'job', 'team_leader', 'collaborators',
                                     'work_size', 'start_date', 'end_date', 'is_finished'))
        }
    )


@blueprint.route('/api/jobs', methods=['POST'])
def create_news():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['job', 'team_leader', 'collaborators',
                  'work_size', 'is_finished']):
        return jsonify({'error': 'Bad request'})
    session = db_session.create_session()
    job = Jobs(
        job=request.json.get('job'),
        team_leader=request.json.get('team_leader'),
        collaborators=request.json.get('collaborators'),
        work_size=request.json.get('work_size'),
        is_finished=request.json.get('is_finished')
    )
    if request.json.get('start_date'):
        job.start_date = request.json.get('start_date')
    if request.json.get('end_date'):
        job.start_date = request.json.get('end_date')
    session.add(job)
    session.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/jobs/<int:job_id>', methods=['DELETE'])
def delete_news(job_id):
    session = db_session.create_session()
    job = session.query(Jobs).get(job_id)
    if not job:
        return jsonify({'error': 'Not found'})
    session.delete(job)
    session.commit()
    return jsonify({'success': 'OK'})
