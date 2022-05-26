from distutils.log import error
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt
from datetime import datetime

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/YYYY-MM-DD  startdate<br/>"
        f"/api/v1.0/YYYY-MM-DD/YYYY-MM-DD range start-end"
    )


@app.route("/api/v1.0/precipitation")
def prcp():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all measurement dates"""
    # Query all measurement
    results = session.query(Measurement.date,Measurement.prcp).all()

    session.close()

    all_prcp = []
    for date,prcp  in results:
        prcp_dct = {
            date: prcp
        }
        all_prcp.append(prcp_dct)

    return jsonify(all_prcp)


@app.route("/api/v1.0/stations")
def names():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all station
    results = session.query(Station.station).all()

    session.close()

    # Convert list of tuples into normal list
    all_names = list(np.ravel(results))

    return jsonify(all_names)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    a = session.query(Measurement.station, func.count(Measurement.station)).group_by('station').order_by(func.count(Measurement.station).desc()).all()
    most_active_stn = a[0][0]

    measurement_last_date = session.query(Measurement).order_by(Measurement.date.desc()).\
    filter(Measurement.station == most_active_stn).first()
    measurement_last_date = datetime.strptime(measurement_last_date.date, '%Y-%m-%d')

    # Calculate the date 1 year ago from the last data point in the database
    query_date = measurement_last_date - dt.timedelta(days=366)

    results = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.date >= query_date).\
    filter(Measurement.station == most_active_stn).all()

    session.close()

    all_tobs = []
    for date,tobs  in results:
        tobs_dct = {
            date: tobs
        }
        all_tobs.append(tobs_dct)

    return jsonify(all_tobs)

@app.route("/api/v1.0/<start>")
def measurement_by_date(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Set our Start date from inputs
    start  = datetime.strptime(start, '%Y-%m-%d')

    # Query the MIN,MAX and Average
    TMIN = session.query(func.min(Measurement.tobs)).\
    filter(Measurement.date >= start).scalar()

    TMAX = session.query(func.max(Measurement.tobs)).\
    filter(Measurement.date >= start).scalar()

    TAVG = session.query(func.avg(Measurement.tobs)).\
    filter(Measurement.date >= start).scalar()
    TAVG = round(TAVG,2)

    session.close()

    all_tobs = []

    dict_ = {}
    dict_['StartDate'] = start
    dict_['TMIN'] = TMIN
    dict_['TMAX'] = TMAX
    dict_['TAVG'] = TAVG

    all_tobs.append(dict_)

    try:
        return jsonify(all_tobs)
    except ValueError:
        return jsonify({"error": "Date not found."}), 404

@app.route("/api/v1.0/<start>/<end>")
def measurement_by_date_start_end(start,end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    print(start, end)

    #Set our Start and end date from inputs
    start  = datetime.strptime(start, '%Y-%m-%d')
    end  = datetime.strptime(end, '%Y-%m-%d')

    #QUery minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    TMIN = session.query(func.min(Measurement.tobs)).\
    filter(Measurement.date <= end, Measurement.date >= start).scalar()

    TMAX = session.query(func.max(Measurement.tobs)).\
    filter(Measurement.date >= start, Measurement.date <= end).scalar()

    TAVG = session.query(func.avg(Measurement.tobs)).\
    filter(Measurement.date >= start, Measurement.date <= end).scalar()
    TAVG = round(TAVG,2)

    session.close()

    all_tobs = []

    dict_ = {}
    dict_['StartDate'] = start
    dict_['EndDate'] = end
    dict_['TMIN'] = TMIN
    dict_['TMAX'] = TMAX
    dict_['TAVG'] = TAVG

    all_tobs.append(dict_)

    try:
        return jsonify(all_tobs)
    except ValueError:
        return jsonify({"error": "Date not found."}), 404

if __name__ == '__main__':
    app.run(debug=True)

