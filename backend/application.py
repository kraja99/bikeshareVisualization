import sys
import os
import psycopg2
from flask import Flask, jsonify
from flask_restful import Api, Resource, reqparse
from flask_cors import CORS

application = Flask(__name__)
api = Api(application)
CORS(application)
connect_str = "dbname='{}' user='{}' host='{}' password='{}' port='{}'".format(os.environ['RDS_DB_NAME'], os.environ['RDS_USERNAME'], os.environ['RDS_HOSTNAME'], os.environ['RDS_PASSWORD'], int(os.environ['RDS_PORT']))
conn = psycopg2.connect(connect_str)

# queries Lat and Long given a station id
class getLatLong(Resource):
    def get(self, station):
        conn = getConn()
        cursor = conn.cursor()
        result = {}

        sql_command = """SELECT station_lat, station_long FROM station WHERE station_id={mystation};""".format(mystation = station)
        cursor.execute(sql_command)
        result['LatLong'] = cursor.fetchall()[0]

        result = jsonify(result)
        result.status_code = 200
        cursor.close()
        return result

# gets list of all stations in db
class getStations(Resource):
    def get(self):
        conn = getConn()
        cursor = conn.cursor()
        result = {}

        sql_command = """SELECT station_id FROM station WHERE station_id!=3000 AND station_id!=4108;"""
        cursor.execute(sql_command)
        result['Stations'] = cursor.fetchall()

        result = jsonify(result)
        result.status_code = 200
        cursor.close()
        return result

# query season data as well as checkin checkout data
class timeData(Resource):
    def get(self):
        conn = getConn()
        cursor = conn.cursor()
        result = {}

        result['DurationBySeason'] = []
        sql_command = """SELECT (AVG(duration) FILTER (WHERE date_part('month', start_time) = 3 OR date_part('month', start_time) = 4 OR date_part('month', start_time) = 5))::float AS Spring,
            (AVG(duration) FILTER (WHERE date_part('month', start_time) = 6 OR date_part('month', start_time) = 7 OR date_part('month', start_time) = 8))::float AS Summer,
            (AVG(duration) FILTER (WHERE date_part('month', start_time) = 9 OR date_part('month', start_time) = 10 OR date_part('month', start_time) = 11))::float AS Fall,
            (AVG(duration) FILTER (WHERE date_part('month', start_time) = 12 OR date_part('month', start_time) = 1 OR date_part('month', start_time) = 2))::float AS Winter
            FROM trip WHERE duration!=86400;"""
        cursor.execute(sql_command)
        result['DurationBySeason'].append(cursor.fetchall()[0])

        result['PassholderCountBySeason'] = []
        # Consolidated all passholder season counts into one query
        sql_command = """SELECT COUNT(*) FILTER (WHERE passholder_type = 'Monthly Pass' AND (date_part('month', start_time) = 3 OR date_part('month', start_time) = 4 OR date_part('month', start_time) = 5)) AS MonthlySpring,
            COUNT(*) FILTER (WHERE passholder_type = 'Monthly Pass' AND (date_part('month', start_time) = 6 OR date_part('month', start_time) = 7 OR date_part('month', start_time) = 8)) AS MonthlySummer,
            COUNT(*) FILTER (WHERE passholder_type = 'Monthly Pass' AND (date_part('month', start_time) = 9 OR date_part('month', start_time) = 10 OR date_part('month', start_time) = 11)) AS MonthlyFall,
            COUNT(*) FILTER (WHERE passholder_type = 'Monthly Pass' AND (date_part('month', start_time) = 12 OR date_part('month', start_time) = 1 OR date_part('month', start_time) = 2)) AS MonthlyWinter,
            COUNT(*) FILTER (WHERE passholder_type = 'Staff Annual' AND (date_part('month', start_time) = 3 OR date_part('month', start_time) = 4 OR date_part('month', start_time) = 5)) AS StaffSpring,
            COUNT(*) FILTER (WHERE passholder_type = 'Staff Annual' AND (date_part('month', start_time) = 6 OR date_part('month', start_time) = 7 OR date_part('month', start_time) = 8)) AS StaffSummer,
            COUNT(*) FILTER (WHERE passholder_type = 'Staff Annual' AND (date_part('month', start_time) = 9 OR date_part('month', start_time) = 10 OR date_part('month', start_time) = 11)) AS StaffFall,
            COUNT(*) FILTER (WHERE passholder_type = 'Staff Annual' AND (date_part('month', start_time) = 12 OR date_part('month', start_time) = 1 OR date_part('month', start_time) = 2)) AS StaffWinter,
            COUNT(*) FILTER (WHERE passholder_type = 'Flex Pass' AND (date_part('month', start_time) = 3 OR date_part('month', start_time) = 4 OR date_part('month', start_time) = 5)) AS FlexSpring,
            COUNT(*) FILTER (WHERE passholder_type = 'Flex Pass' AND (date_part('month', start_time) = 6 OR date_part('month', start_time) = 7 OR date_part('month', start_time) = 8)) AS FlexSummer,
            COUNT(*) FILTER (WHERE passholder_type = 'Flex Pass' AND (date_part('month', start_time) = 9 OR date_part('month', start_time) = 10 OR date_part('month', start_time) = 11)) AS FlexFall,
            COUNT(*) FILTER (WHERE passholder_type = 'Flex Pass' AND (date_part('month', start_time) = 12 OR date_part('month', start_time) = 1 OR date_part('month', start_time) = 2)) AS FlexWinter,
            COUNT(*) FILTER (WHERE passholder_type = 'Walk-up' AND (date_part('month', start_time) = 3 OR date_part('month', start_time) = 4 OR date_part('month', start_time) = 5)) AS WalkSpring,
            COUNT(*) FILTER (WHERE passholder_type = 'Walk-up' AND (date_part('month', start_time) = 6 OR date_part('month', start_time) = 7 OR date_part('month', start_time) = 8)) AS WalkSummer,
            COUNT(*) FILTER (WHERE passholder_type = 'Walk-up' AND (date_part('month', start_time) = 9 OR date_part('month', start_time) = 10 OR date_part('month', start_time) = 11)) AS WalkFall,
            COUNT(*) FILTER (WHERE passholder_type = 'Walk-up' AND (date_part('month', start_time) = 12 OR date_part('month', start_time) = 1 OR date_part('month', start_time) = 2)) AS WalkWinter										  
            FROM trip WHERE duration!=86400;"""
        cursor.execute(sql_command)
        result['PassholderCountBySeason'].append(cursor.fetchall()[0])

        result['CheckoutCount'] = []
        result['CheckinCount'] = []
        for i in range(24): # query counts of rides that were checked in/out during each hour
            sql_command = """SELECT Count(*) FROM trip WHERE start_time::time >= '{start_hr}:00:00' AND start_time::time < '{end_hr}:00:00';""".format(start_hr=i, end_hr=i+1)
            cursor.execute(sql_command)
            result['CheckoutCount'].append(cursor.fetchall()[0][0])
            sql_command = """SELECT Count(*) FROM trip WHERE end_time::time >= '{start_hr}:00:00' AND end_time::time < '{end_hr}:00:00';""".format(start_hr=i, end_hr=i+1)
            cursor.execute(sql_command)
            result['CheckinCount'].append(cursor.fetchall()[0][0])

        result = jsonify(result)
        result.status_code = 200
        cursor.close()
        return result

class initialData(Resource):
    def get(self):
        conn = getConn()
        cursor = conn.cursor()
        result = {}

        sql_command = """SELECT start_station_id, Count(start_station_id) FROM trip GROUP BY start_station_id ORDER BY Count(start_station_id) DESC LIMIT 5;"""
        cursor.execute(sql_command)
        result['MostPopularStartStation'] = cursor.fetchall()

        sql_command = """SELECT end_station_id, Count(end_station_id) FROM trip GROUP BY end_station_id ORDER BY Count(end_station_id) DESC LIMIT 5;"""
        cursor.execute(sql_command)
        result['MostPopularEndStation'] = cursor.fetchall()

        sql_command = """SELECT AVG(distance) FILTER (WHERE distance > 0) FROM trip WHERE route_category = 'One Way';"""
        cursor.execute(sql_command)
        result['AverageOneWayDistance'] = cursor.fetchall()[0][0]

        sql_command = """SELECT AVG((duration::float/3600) * 7) FROM trip WHERE start_station_id = end_station_id AND distance >= 0 AND duration != 86400;"""
        cursor.execute(sql_command)
        result['AverageRoundtripDistance'] = cursor.fetchall()[0][0]

        sql_command = """SELECT start_station_id, end_station_id, count(*) as RouteCount FROM trip GROUP BY start_station_id, end_station_id Order by routecount DESC LIMIT 10;"""
        cursor.execute(sql_command)
        result['MostPopularRoutes'] = cursor.fetchall()
        sql_command = """SELECT start_station_id, end_station_id, count(*) as RouteCount FROM trip GROUP BY start_station_id, end_station_id Order by routecount DESC LIMIT 10;"""
        cursor.execute(sql_command)
        result['MostPopularRoutes'] = cursor.fetchall()

        temp = []
        sql_command ="""SELECT Count(*) FROM trip WHERE passholder_type='Walk-up' AND duration <= 900;"""
        cursor.execute(sql_command)
        temp.append(cursor.fetchall()[0][0])
        sql_command ="""SELECT Count(*) FROM trip WHERE passholder_type='Walk-up' AND duration > 900 AND duration <= 2700;"""
        cursor.execute(sql_command)
        temp.append(cursor.fetchall()[0][0])
        sql_command ="""SELECT Count(*) FROM trip WHERE passholder_type='Walk-up' AND duration > 2700;"""
        cursor.execute(sql_command)
        temp.append(cursor.fetchall()[0][0])
        sql_command ="""SELECT Count(*) FROM trip WHERE passholder_type!='Walk-up' AND duration <= 900;"""
        cursor.execute(sql_command)
        temp.append(cursor.fetchall()[0][0])
        sql_command ="""SELECT Count(*) FROM trip WHERE passholder_type!='Walk-up' AND duration > 900 AND duration <= 2700;"""
        cursor.execute(sql_command)
        temp.append(cursor.fetchall()[0][0])
        sql_command ="""SELECT Count(*) FROM trip WHERE passholder_type!='Walk-up' AND duration > 2700;"""
        cursor.execute(sql_command)
        temp.append(cursor.fetchall()[0][0])
        result['Duration_Walkup'] = []
        result['Duration_Walkup'].append(temp[0])
        result['Duration_Walkup'].append(temp[1])
        result['Duration_Walkup'].append(temp[2])
        result['Duration_Non_Walkup'] = []
        result['Duration_Non_Walkup'].append(temp[3])
        result['Duration_Non_Walkup'].append(temp[4])
        result['Duration_Non_Walkup'].append(temp[5])

        sql_command = """SELECT Count(*) FROM trip WHERE passholder_type!='Walk-up';"""
        cursor.execute(sql_command)
        result['RegularUsers'] = cursor.fetchall()[0][0]

        result = jsonify(result)
        result.status_code = 200
        cursor.close()
        return result

# Try to reconnect to database if we lose connection
def getConn():
    global conn
    if not conn or conn.closed:
        print ("Stale connection, trying to reconnect...")
        conn = psycopg2.connect(connect_str)
    return conn

# API endpoints
api.add_resource(getLatLong, '/getLatLong/<string:station>')
api.add_resource(getStations, '/getStations')
api.add_resource(timeData, '/timeData')
api.add_resource(initialData, '/initialData')