from functools import wraps
from flask import request, jsonify
from .config import Config
from .database import mydb
import jwt

cur = mydb.cursor()

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
			data = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
		except:
			return jsonify(Error="Token is invalid")

		return f(*args, **kwargs)
	return decorator

def get_company_name(id):
	q = """ SELECT * FROM companies WHERE id = '%s' """ % id
	cur.execute(q)
	data = cur.fetchone()

	return data[1]

def get_employee_data(id):
	q = """ SELECT * FROM employees WHERE id = '%s' """ % id
	cur.execute(q)
	data = cur.fetchall()
	if(len(data) < 1):
		return "none"
	else:
		return data[0]
		
def get_user_data(id):
	q = """ SELECT * FROM users WHERE id = '%s' """ % id
	cur.execute(q)
	data = cur.fetchall()
	if(len(data) < 1):
		return "none"
	else:
		return data[0]
