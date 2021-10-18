from flask import Blueprint, render_template, request, jsonify
from .database import mydb
from .functions import get_company_name

frontend = Blueprint("frontend", __name__)
cur = mydb.cursor()

@frontend.route("/")
def home():
	return render_template('index.html')

@frontend.route("/requests")
def get_requests():
	company_id = request.args.get("company_id")
	if(company_id):
		query = """ SELECT * FROM requests WHERE company_id = '%s' """ % company_id
	else:
		query = """ SELECT * FROM requests """

	cur.execute(query)
	data = cur.fetchall()
	r = []
	for x in data:
		company_name = get_company_name(x[0])
		req = (x[0], x[1], x[2], company_name, x[4])
		r.append(req)

	return render_template('requests.html', requests=r)
