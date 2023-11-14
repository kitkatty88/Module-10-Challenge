# Import the dependencies.
from flask import Flask, jsonify

import datetime as dt
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    return (
        f"Hello! Welcome to the Hawaii Weather Analysis!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"In the end and start date options, please replace the start and end with the date in the format of MMDDYYYY <br/>"
        f"/api/v1.0/temp/start<br/>"
        f"/api/v1.0/temp/start/end"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    
    # Query for the precipitation
    pastdate = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    precipitation = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= pastdate).all()

    session.close()
    
    # Create a dictionary to hold the data
    
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)


@app.route("/api/v1.0/stations")
def stations():

    # Query for the stations
    all_stations = session.query(Station.station).all()

    session.close()

    # convert all_stations into a list
    
    stations = list(np.ravel(all_stations))
    return jsonify(stations=stations)


@app.route("/api/v1.0/tobs")
def temp_monthly():
    
    # Query for the tobs
    pastdate = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    mostactive = "USC00519281"

    tobs = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == mostactive).filter(Measurement.date >= pastdate).all()

    session.close()
    
    # convert into list
    
    temps = list(np.ravel(tobs))
    return jsonify(temps=temps)


@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")

def temperature(start=None, end=None):

    # select statement for min, max, and avg
    sel = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs),]

    start = dt.datetime.strptime(start, "%m%d%Y").date()
    end = dt.datetime.strptime(end, "%m%d%Y").date()

    result_stats = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    
    if not end:
        start = dt.datetime.strptime(start, "%m%d%Y").date()
        result_stats = session.query(*sel).\
            filter(Measurement.date >= start).all()

        session.close()

        temps = list(np.ravel(result_stats))
        return jsonify(temps)
    
    session.close()

   # convert to a list
    temps = list(np.ravel(result_stats))
    return jsonify(temps=temps)


if __name__ == '__main__':
    app.run()