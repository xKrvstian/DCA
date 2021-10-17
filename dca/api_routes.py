from flask import Blueprint,jsonify
from .database import mydb
from .functions import *
from .config import Config
import bcrypt
import datetime

cur = mydb.cursor()

api = Blueprint("api", __name__)

@api.route("/companies")
@token_required
def get_companies():
	cur.execute("SELECT * FROM companies")
	data = sql_to_json(cur)

	return jsonify(Data=data)

@api.route("/companies/<company_id>")
@token_required
def get_company(company_id):
	query = """ SELECT * FROM companies WHERE id = %s """ % int(company_id)
	cur.execute(query)

	data = sql_to_json(cur)
	if(data == 1):
		return jsonify(Error="No company found with given ID"), 401
	else:
		return jsonify(Data=data)

@api.route("/login", methods=['POST'])
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
			token = jwt.encode({'id':data[0], 'username':data[1], 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=1440)}, Config.SECRET_KEY, "HS256")
			return jsonify(Token=token)
		else:
			return jsonify(Error="Invalid username or password"), 401


