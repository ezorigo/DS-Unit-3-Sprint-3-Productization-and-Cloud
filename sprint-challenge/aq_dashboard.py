"""OpenAQ Air Quality Dashboard with Flask."""

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import openaq

APP = Flask(__name__)

APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
DB = SQLAlchemy(APP)


class Record(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    datetime = DB.Column(DB.String(25))
    value = DB.Column(DB.Float, nullable=False)

    def __repr__(self):            
        return 'UTC: {} ---> Value(µg/m³): {}'.format(self.datetime, self.value)


@APP.route('/')
def root():
    records = Record.query.filter(Record.value>=10).all()
    return render_template('base.html', title='Home', records=records)

@APP.route('/refresh')
def refresh():
    """Pull fresh data from Open AQ and replace existing data."""
    DB.drop_all()
    DB.create_all()
    # TODO Get data from OpenAQ, make Record objects with it, and add to db
    api = openaq.OpenAQ()
    status, body = api.measurements(city='Los Angeles', parameter='pm25')
    results = body['results']
    for result in results:
        db_record = Record(datetime=str(result['date']['utc']), value=str(result['value']))
        DB.session.add(db_record)
    DB.session.commit()
    return 'Data refreshed!'