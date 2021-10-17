from flask import Flask, jsonify, Response, request
from functools import wraps
import mysql.connector
import json
import jwt
import bcrypt
import datetime

mydb = mysql.connector.connect(
	host="localhost",
	user="dca",
	password="7asdhk12",
	database="dca"
)

cur = mydb.cursor()

app = Flask(__name__)

def sql_to_json(cur):
	rv = cur.fetchall()
	if(len(rv) < 1):
		return 1
	headers = [x[0] for x in cur.description]
	json_data = []
	for result in rv:
		json_data.append(dict(zip(headers, result)))
	
	return json_data

def token_required(f):
	@wraps(f)
	def decorator(*args, **kwargs):
		token = None
		if 'Authorization' in request.headers:
			token = request.headers['Authorization']

		if not token:
			return jsonify(Error="A valid token is missing")

		try:
			data = jwt.decode(token, "test", algorithms=["HS256"])
		except:
			return jsonify(Error="Token is invalid")

		return f(*args, **kwargs)
	return decorator

@app.route("/login", methods=['POST'])
def login_user():
	user_login = request.form.get("username")
	user_pass = request.form.get("password")

	query = """ SELECT * FROM users WHERE username = '%s' """ % user_login
	cur.execute(query)
	result = cur.fetchall()

	if(len(result) < 1):
		return jsonify(Error="Invalid username or password"), 401
	else:
		data = result[0]
		hashed = data[4]
		#token = jwt.encode({'id' : data[0], 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=45)}, 'test', "HS256")a
		if(bcrypt.checkpw(str.encode(user_pass), str.encode(hashed))):
			token = jwt.encode({'id':data[0], 'username':data[1], 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=1440)}, 'test', "HS256")
			return jsonify(Token=token)
		else:
			return jsonify(Error="Invalid username or password"), 401

@app.route("/api/companies")
@token_required
def get_companies():
	cur.execute("SELECT * FROM companies")
	data = sql_to_json(cur)

	return jsonify(Data=data)

@app.route("/api/companies/<company_id>")
@token_required
def get_company(company_id):

	app.logger.info(company_id)
	
	query = """ SELECT * FROM companies WHERE id = %s """ % int(company_id)
	cur.execute(query)

	data = sql_to_json(cur)
	if(data == 1):
		return jsonify(Error="No company found with given ID"), 401
	else:
		return jsonify(Data=data)

if __name__ == '__main__':
	app.run()
