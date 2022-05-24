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
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def prcp():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all passenger names"""
    # Query all passengers
    results = session.query(Measurement.date,Measurement.prcp).all()

    session.close()

    all_prcp = []
    for date,prcp  in results:
        prcp_dct = {
            date: prcp
        }
        #prcp_dct['date'] = date
        #prcp_dct['prcp'] = prcp
        all_prcp.append(prcp_dct)

    # Convert list of tuples into normal list
    #all_names = list(np.ravel(results))

    return jsonify(all_prcp)


@app.route("/api/v1.0/stations")
def names():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of passenger data including the name, age, and sex of each passenger"""
    # Query all passengers
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

    # Convert list of tuples into normal list
    #all_names = list(np.ravel(results))

    return jsonify(all_tobs)

if __name__ == '__main__':
    app.run(debug=True)

