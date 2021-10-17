from functools import wraps
from flask import request, jsonify
from .config import Config
import jwt

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
