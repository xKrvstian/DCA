from flask import Blueprint, render_template, request, jsonify
from .database import mydb
from .functions import get_company_name, get_employee_data

frontend = Blueprint("frontend", __name__)
cur = mydb.cursor(dictionary=True)

@frontend.route("/")
def home():
	cur.execute("SELECT * FROM companies")
	data = cur.fetchall()

	emp_data = {}
	open_tasks_data = {}
	waiting_tasks_data = {}
	closed_tasks_data = {}

	for x in data:
		id = x['id']
		q = """ SELECT * FROM employees WHERE company_id = '%s' """ % id
		cur.execute(q)
		e = cur.fetchall()
		emp = len(e)
		emp_data[x['name']] = emp

		q = """ SELECT * FROM requests WHERE company_id = '%s' """ % id
		cur.execute(q)
		e = cur.fetchall()
		open = 0
		waiting = 0
		closed = 0
		for r in e:
			if(r['status'] == "OPEN"):
				open += 1
			elif(r['status'] == "WAITING"):
				waiting += 1
			elif(r['status'] == "CLOSED"):
				closed += 1
		open_tasks_data[x['name']] = open
		closed_tasks_data[x['name']] = closed
		waiting_tasks_data[x['name']] = waiting
	return render_template('index.html', data=data, emp_data=emp_data, open=open_tasks_data, closed=closed_tasks_data, waiting=waiting_tasks_data)

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
		company_name = get_company_name(x['company_id'])
		emp = get_employee_data(x['employee_id'])
		if(emp == "none"):
			employee = x['employee_id']
		else:
			employee = "%s %s" % (emp[1], emp[2])
		req = (x['id'], x['date'], x['title'], company_name, employee, x['status'])
		r.append(req)

	return render_template('requests.html', requests=r)

@frontend.route("/requests/<req_id>")
def get_request(req_id):
	query = """ SELECT * FROM requests WHERE id = '%s' """ % req_id
	cur.execute(query)
	data = cur.fetchall()
	if(len(data) < 1):
		req_data = "none"
	else:
		req_data = data[0]

	return render_template("request.html", req_data=req_data)
