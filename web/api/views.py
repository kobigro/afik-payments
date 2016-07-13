from flask import Blueprint, request, url_for
from app import app
from decorators import json, crossdomain
from models import School
from sqlalchemy.orm import joinedload
import payments_service

api = Blueprint('api', __name__)

@app.after_request
def after_request(response):
    print(response)
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

@api.route('/schools/')
@json()
def schools_filter():
    query = School.query
    search_query = request.args.get('q')
    if search_query is not None:
        query = query.filter(
            School.name.like('%{}%'.format(search_query)))

    city = request.args.get('city')
    if city is not None:
        query = query.filter_by(city=city)

    supervision = request.args.get('supervision')
    if supervision is not None:
        query = query.filter_by(supervision=supervision)

    filtered_schools = query.all()
    return [{"short_desc": str(school), "id": school.id} for school in filtered_schools]


@api.route('/schools/<int:school_id>/payments')
@json()
def school(school_id):
    class_name = request.args.get("class")
    payments = payments_service.get_payments(school_id, class_name)
    return payments
