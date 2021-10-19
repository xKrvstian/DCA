from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from .database import mydb
from .functions import get_company_name, get_employee_data, get_user_data
import datetime

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
		company = get_company_name(req_data['company_id'])
		emp = get_employee_data(req_data['employee_id'])
		if(emp == "none"):
			employee = req_data['employee_id']
		else:
			employee = "%s %s" % (emp[1], emp[2])

		req_data['employee'] = employee
		req_data['company'] = company
		
	query = """ SELECT * FROM notes WHERE request_id = '%s' """ % req_id
	cur.execute(query)
	data = cur.fetchall()
	notes = []
	if(len(data) < 1):
		note = "none"
	else:
		note = data
		for n in note:
			user = get_user_data(n['author'])
			notes.append((n['id'], user[1], n['date'], n['note']))

	return render_template("request.html", req_data=req_data, notes=notes)

@frontend.route("/requests/<req_id>/addnote", methods=['POST'])
def add_note(req_id):
	user_id = 1
	note = request.form.get("note_body")
	x = datetime.datetime.now()
	date = x.strftime("%Y-%m-%d %H:%M:%S")
	query = """ INSERT INTO notes(request_id, author, date, note) VALUES('%s', '%s', '%s', '%s') """ % (req_id, user_id, date, note)
	
	cur.execute(query)
	mydb.commit()
	url = "/requests/%s" % req_id
	
	return redirect(url_for('frontend.get_request', req_id=req_id), 302)
	
@frontend.route("/requests/<req_id>/update", methods=['GET', 'POST'])
def edit_request(req_id):
	if(request.method == "GET"):
		query = """ SELECT * FROM requests WHERE id = '%s' """ % req_id
		cur.execute(query)
		data = cur.fetchall()
		if(len(data) < 1):
			req_data = "none"
		else:
			req_data = data[0]
			company = get_company_name(req_data['company_id'])
			emp = get_employee_data(req_data['employee_id'])
			if(emp == "none"):
				employee = req_data['employee_id']
			else:
				employee = "%s %s" % (emp[1], emp[2])

			req_data['employee'] = employee
			req_data['company'] = company

		return render_template("updaterequest.html", req_data=req_data)
	elif(request.method == "POST"):
		status = request.form.get("state")
		body = request.form.get("body")
		query = """ UPDATE requests SET body='%s',status='%s' WHERE id='%s' """ % (body, status, req_id)
		url = "/requests/%s" % req_id
		cur.execute(query)
		mydb.commit()
		
		return redirect(url_for('frontend.get_request', req_id=req_id), 302)
		
@frontend.route("/requests/<req_id>/notes/<note_id>/delete")
def delete_note(req_id, note_id):
	query = """ DELETE FROM notes WHERE id = '%s' """ % note_id
	cur.execute(query)
	mydb.commit()

	url = "/requests/%s" % req_id
	return redirect(url_for('frontend.get_request', req_id=req_id), 302)
