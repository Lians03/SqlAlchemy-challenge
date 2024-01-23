# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy.inspection import inspect
import datetime as dt

# Database Setup
Base = automap_base()

# reflect an existing database into a new model
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect the tables
Base.prepare(autoload_with= engine)


# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)


# Flask Setup
app = Flask(__name__)


# Flask Routes
@app.route("/")
def main():
    return(f"Welcome to the Climate App. <br>"
           f"Below are the available routes: <br>"
           "-------------------------------------<br>"
           f"/api/v1.0/precipitation <br>"
           f"/api/v1.0/stations <br>"
           f"/api/v1.0/tobs <br>"
           f"/api/v1.0/type in your start date <br>"
           f"/api/v1.0/type in your start date/type in your end date <br>"
           )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    measure_result = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).order_by(Measurement.date).all()
    session.close()

    precipitation_dict = {}
    precipitation_dict = dict(measure_result)
    return jsonify(precipitation_dict)

# @app.route("/api/v1.0/stations")
# def stations():
#     session = Session(engine)
#     station_result = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()
#     session.close()

#     output = []
#     for station,name,latitude,longitude,elevation in station_result:
#         station_dict = {}
#         station_dict['station'] = station
#         station_dict['name'] = name
#         station_dict['latitude'] = latitude
#         station_dict['longitude'] = longitude
#         station_dict['elevation'] = elevation
#         output.append(station_dict)

#     return jsonify(output)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    station_result = session.query(Station.name).all()
    session.close()

    output = []
    for record in station_result:
        output.append(record.name)

    return jsonify(output)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    results_active_station = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station=='USC00519281').filter(Measurement.date>='2016-08-23').all()

    session.close()

    output = []
    for date, tobs in results_active_station:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        output.append(tobs_dict)
 
    return jsonify(output)

@app.route("/api/v1.0/<start>")
def temperature(start):
    try:
        # Validate date format form chatgpt
        dt.datetime.strptime(start, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": f"Date format should be YYYY-MM-DD. You entered: {start}"}), 400

    session = Session(engine)

    start_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    session.close()
    
    output = []
    for TMIN, TAVG, TMAX in start_results:
       temp_dict = {} 
       temp_dict["Minimum Temperature"] = TMIN
       temp_dict["Average Temperature"] = TAVG
       temp_dict["Maximum Temperature"] = TMAX
       output.append(temp_dict)

    return jsonify(output)


@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    try:
        # Validate date format form chatgpt
        dt.datetime.strptime(start, '%Y-%m-%d')
        dt.datetime.strptime(end, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": f"Date format should be YYYY-MM-DD. You entered: {start} and {end}"}), 400
    
    session = Session(engine)
    start_end_result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    
    session.close()

    output = []
    for TMIN, TAVG, TMAX in start_end_result:
       new_temp_dict = {} 
       new_temp_dict["Minimum Temperature"] = TMIN
       new_temp_dict["Average Temperature"] = TAVG
       new_temp_dict["Maximum Temperature"] = TMAX
       output.append(new_temp_dict)

    return jsonify(output)




if __name__ == "__main__":
    app.run(debug=True)


