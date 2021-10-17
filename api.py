from flask import Flask, jsonify, Response
import mysql.connector
import json

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

@app.route("/api/companies")
def get_companies():
	cur.execute("SELECT * FROM companies")
	data = sql_to_json(cur)

	return jsonify(Data=data)

@app.route("/api/companies/<company_id>")
def get_company(company_id):
	
	query = """ SELECT * FROM companies WHERE id = %s """ % int(company_id)
	cur.execute(query)

	data = sql_to_json(cur)
	if(data == 1):
		return jsonify(Error="No company found with given ID"), 401
	else:
		return jsonify(Data=data)

if __name__ == '__main__':
	app.run()
