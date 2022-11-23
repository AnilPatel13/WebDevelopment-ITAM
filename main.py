from flask import Flask, render_template, request, redirect, url_for, session, flash
import pyotp
import qrcode
import io
from base64 import b64encode
from module.BaseClass import *
from helper.Constant import *
from collections import OrderedDict
from ordered_set import OrderedSet
import logging as log
import google.cloud.logging as logging

app = Flask(__name__)

app.secret_key = 'Tiger123'


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html")


@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        login_email = request.form.get("loginemailid")
        login_password = request.form.get("logininputPassword")
        base_object = BaseClass()
        data_list = [login_email, login_password]
        account_status = base_object.get_login_data(data_list)
        del base_object
        print(account_status)
        if len(account_status) == 0:
            flash("Invalid Credentails !", "danger")
            return render_template('login.html')
        elif len(account_status) == 1 and account_status[0]['status'] in ('approved', 'reject', 'pending') \
                and account_status[0]['role'] in ('view', 'admin'):
            print("inside")
            account_id = account_status[0]['employee_id']
            user_name = account_status[0]['first_name']
            secret_key = account_status[0]['otp_encoder']
            qr_code = account_status[0]['qr_code']
            role = account_status[0]['role']
            status = account_status[0]['status']
            session['loggedin'] = True
            session['id'] = account_id
            session['username'] = user_name
            session['role'] = role
            session['status'] = status
            decoded_qr_code = b64encode(qr_code).decode("utf-8")
            return render_template('authentication.html', secret=secret_key, image=decoded_qr_code)
    elif request.method == "GET" and 'loggedin' in session and '2fa' in session and \
            (session['role'] in ['view', 'admin'] and session['status'] in ['approved', 'pending', 'reject']):
        return redirect(url_for('home_page'))
    elif request.method == "GET":
        return render_template('login.html')
    else:
        render_template("404.html")


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/forget_password', methods=['GET', 'POST'])
def forget_password():
    if request.method == "POST":
        login_email = request.form.get("forgetinputEmail")
        login_password = request.form.get("inputPassword")

        # check terms and condition checkbox
        if not request.form.get('forgetpswterms'):
            flash("Please Accept the Terms and Condition !", "danger")
            return render_template('forget_password.html')

        base_object = BaseClass()

        # check email exist
        data_list = [login_email.lower()]
        email_status = base_object.check_email_exist(data_list)
        if not email_status:
            flash("Email Address does not exist !", "danger")
            del base_object
            return render_template('forget_password.html')

        # updating the database for the password reset
        data_list = [login_password, login_email]
        update_status = base_object.update_password(data_list)
        del base_object
        if update_status:
            session.clear()
            return redirect(url_for('login'))
        else:
            flash("Old and New password is Same !", "danger")
            return render_template('forget_password.html')
    elif request.method == "GET":
        return render_template('forget_password.html')
    else:
        render_template("404.html")


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == "POST":
        firstName = request.form.get("firstName")
        middleName = request.form.get("middleName")
        lastName = request.form.get("lastName")
        inputEmail = request.form.get("inputEmail")
        typePhone = request.form.get("typePhone")
        birthday = request.form.get("birthday")
        inputPassword = request.form.get("inputPassword")

        base_object = BaseClass()

        # check email is already taken
        data_list = [inputEmail.lower()]
        email_status = base_object.check_email_exist(data_list)
        if email_status:
            flash("Email address is already Taken !", "danger")
            del base_object
            return render_template('register.html')

        data_list = [firstName, middleName, lastName, inputEmail, birthday]
        account_status = base_object.check_user_exist(data_list)
        # check account exist
        if account_status:
            flash("User is Already Registered !", "danger")
            del base_object
            return render_template('register.html')

        # Storing the user data to database.
        secret = pyotp.random_base32()
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(inputEmail, issuer_name=PROJECT.PROJECT_NAME)
        qr_code = qrcode.make(totp_uri)
        qr_data = io.BytesIO()
        qr_code.save(qr_data, "PNG")
        qr_code_binary = qr_data.getvalue()
        data_list = [firstName, middleName, lastName, inputEmail, typePhone, birthday, inputPassword, secret,
                     qr_code_binary]
        user_creation_status = base_object.insert_new_user(data_list)
        del base_object
        if user_creation_status:
            return render_template('login.html')
    elif request.method == "GET":
        return render_template('register.html')
    else:
        render_template("404.html")


@app.route('/authentication', methods=["POST", "GET"])
def authentication():
    if request.method == "POST" and 'loggedin' in session:
        input_otp = request.form.get("inputOTP")
        base_object = BaseClass()
        employee_id = session['id']
        first_name = session['username']
        data_list = [first_name, employee_id]
        account_status = base_object.get_user_data(data_list)
        secret_key = account_status[0]['otp_encoder']
        qr_code = account_status[0]['qr_code']
        decoded_qr_code = b64encode(qr_code).decode("utf-8")
        totp = pyotp.TOTP(secret_key)

        del base_object
        if not totp.verify(input_otp):
            flash("Invalid OTP !", "danger")
            return render_template('authentication.html', secret=secret_key, image=decoded_qr_code)
        else:
            session['2fa'] = True
            return redirect(url_for('home_page'))
    elif request.method == "GET" and 'loggedin' in session and '2fa' in session:
        return redirect(url_for('home_page'))
    elif request.method == "GET":
        return redirect(url_for('logout'))
    else:
        render_template("404.html")


@app.route('/home_page', methods=["GET"])
def home_page():
    if request.method == "GET" and 'loggedin' in session and '2fa' in session and \
            (session['role'] in ['view', 'admin'] and session['status'] in ['approved', 'pending', 'reject']):
        base_object = BaseClass()
        asset_count = base_object.get_all_asset_count([])
        asset_retired_count = base_object.get_all_asset_retired_count([])
        asset_request_count = base_object.get_all_asset_request_count([])
        support_ticket_count = base_object.get_all_support_count([])
        stockroom_count = base_object.get_all_stockroom_count([])
        request_fulfillment_count = base_object.get_all_request_fulfillment_count([])
        asset_7days_details = base_object.get_all_asset_details_7days([])
        area_map_labels = []
        area_map_value = []
        for object in asset_7days_details:
            area_map_labels.append(object['creation_date'])
            area_map_value.append(object['count'])

        request_fulfillment_365days_details = base_object.get_all_asset_request_fulfillment_365days([])
        bar_graph_labels = []
        bar_graph_value = []
        for object in request_fulfillment_365days_details:
            bar_graph_labels.append(object['month'])
            bar_graph_value.append(object['count'])

        stockroom_detail_count = base_object.get_all_stockroom_counts([])
        pie_chart_labels = []
        pie_chart_value = []
        for object in stockroom_detail_count:
            pie_chart_labels.append(object['building'])
            pie_chart_value.append(object['count'])

        support_request_count_all = base_object.get_all_support_request_count([])
        asset_request_ful_count_all = base_object.get_all_asset_request_ful_count([])
        radar_chart_labels = OrderedSet()
        radar_chart_request_ticket_count = []
        radar_chart_support_ticket_count = []
        for object in support_request_count_all:
            radar_chart_labels.append(object['month'])
            radar_chart_support_ticket_count.append(object['count'])

        for object in asset_request_ful_count_all:
            radar_chart_labels.append(object['month'])
            radar_chart_request_ticket_count.append(object['count'])

        del base_object
        return render_template('index.html', username=session['username'], accountid=session['id'],
                               access_role=session['role'], access_role_status=session['status'],
                               assetCountData=asset_count, assetRetiredCount=asset_retired_count,
                               assetRequestCount=asset_request_count, supportTicketCount=support_ticket_count,
                               stockroomCount=stockroom_count, requestFulfillmentCount=request_fulfillment_count,
                               areaMapLabels=area_map_labels, areaMapValue=area_map_value,
                               barGraphLabels=bar_graph_labels, barGraphValue=bar_graph_value,
                               pieChartLabels=pie_chart_labels, pieChartValue=pie_chart_value,
                               radarChartLabels=list(radar_chart_labels),
                               radarChartRequestTicketCount=radar_chart_request_ticket_count,
                               radarChartSupportTicketCount=radar_chart_support_ticket_count)
    else:
        return redirect(url_for('login'))


@app.route('/add_asset', methods=["POST", "GET"])
def add_asset():
    if request.method == "POST" and 'loggedin' in session and '2fa' in session and \
            (session['role'] == 'admin' and session['status'] == 'approved'):

        base_object = BaseClass()

        # Form
        asset_serailno = request.form.get("serialno")
        asset_tag = request.form.get("taggingid")
        asset_state = request.form.get("assetstate")
        asset_model = request.form.get("assetmodel")
        asset_condition = request.form.get("assetcondition")
        asset_assigned_to = request.form.get("assignedto")
        assetstockroom = request.form.get("assetstockroom")

        asset_state_list = base_object.get_asset_state_id([asset_state])
        asset_state_id = asset_state_list[0]['state_id']

        building_name = assetstockroom.split("-")[0].strip()
        stockroom_room_no = assetstockroom.split("-")[1].strip()

        asset_state_list = base_object.get_stockroom_details([building_name, stockroom_room_no])
        stockroom_room_id = asset_state_list[0]['stockroom_id']

        asset_condition_list = base_object.get_asset_condition_by_id([asset_condition])
        asset_condition_id = asset_condition_list[0]['condition_id']

        assigned_to = None
        employee_id = None
        if asset_assigned_to != "un-assigned":
            employee_details = base_object.get_employee_data_id([asset_assigned_to])
            assigned_to = employee_details[0]['first_name']
            employee_id = employee_details[0]['employee_id']

        data_list = [asset_serailno, asset_state_id, asset_tag, asset_state, building_name, stockroom_room_no,
                     stockroom_room_id, asset_condition, asset_condition_id, asset_model, assigned_to, employee_id
                     ]

        add_asset_status = base_object.add_new_asset_entry(data_list)
        if add_asset_status:
            flash("Successfully Inserted Asset Record", "success")
        else:
            flash("Failed to Insert Asset Record", "danger")

        asset_state = base_object.get_asset_state([])
        asset_condition = base_object.get_asset_condition([])
        stockroom_mgmt = base_object.get_stockroom([])
        employee_id_list = base_object.get_employee_data([])
        employee_details = ["un-assigned"]
        for emp_id in employee_id_list:
            employee_details.append(emp_id['employee_id'])
        del base_object
        return render_template('add_asset.html', username=session['username'], accountid=session['id'],
                               access_role=session['role'], access_role_status=session['status'],
                               assetState=asset_state, assetCondition=asset_condition,
                               stockroomMgmt=stockroom_mgmt, employeeDetails=employee_details)
    elif request.method == "GET" and 'loggedin' in session and '2fa' in session and \
            (session['role'] == 'admin' and session['status'] == 'approved'):
        base_object = BaseClass()
        asset_state = base_object.get_asset_state([])
        asset_condition = base_object.get_asset_condition([])
        stockroom_mgmt = base_object.get_stockroom([])
        employee_id_list = base_object.get_employee_data([])
        employee_details = ["un-assigned"]
        for emp_id in employee_id_list:
            employee_details.append(emp_id['employee_id'])
        del base_object
        return render_template('add_asset.html', username=session['username'], accountid=session['id'],
                               access_role=session['role'], access_role_status=session['status'],
                               assetState=asset_state, assetCondition=asset_condition,
                               stockroomMgmt=stockroom_mgmt, employeeDetails=employee_details)
    elif request.method == "GET" and 'loggedin' in session and '2fa' in session and \
            (session['role'] == 'view' and session['status'] == 'approved') or \
            (session['role'] == 'admin' and session['status'] in ['reject', 'pending']):
        return render_template("insufficient_privileges.html")
    else:
        return render_template("404.html")


@app.route('/request_asset', methods=["POST", "GET"])
def request_asset():
    if request.method == "POST" and 'loggedin' in session and '2fa' in session and \
            (session['role'] in ['view', 'admin'] and session['status'] in ['approved', 'pending', 'reject']):
        service_request_type = "Asset_Request"
        base_object = BaseClass()

        # Form
        employeeid = request.form.get("employeeid")
        assetpriority = request.form.get("assetpriority")
        assetmodel = request.form.get("assetmodel")
        assettag = request.form.get("assettag")
        assetserialno = request.form.get("assetserialno")
        assetunit = request.form.get("assetunit")
        additionalComments = request.form.get("additionalComments")
        if additionalComments == "":
            additionalComments = None
        acceptassetterms = request.form.get("acceptassetterms")

        if acceptassetterms != "Yes":
            flash("Please Check the Terms and Condition !", "danger")
        else:

            ticketno = base_object.get_max_ticket_no([])
            if ticketno == None:
                ticketno = 1001

            user_data = base_object.get_employee_data_id([employeeid])
            employee_name = user_data[0]['first_name']

            asset_priority_data = base_object.get_request_priority_id([assetpriority])
            asset_priority_id = asset_priority_data[0]['id']

            asset_data = base_object.get_asset_data_by_srn_tag_model([assetserialno, assettag, assetmodel])
            asset_id = asset_data[0]['asset_id']

            data_dict = {
                "query1": [ticketno, employee_name, employeeid, asset_priority_id, assetpriority, asset_id, assetmodel,
                           assettag,
                           assetserialno, assetunit, additionalComments
                           ],
                "query2": [ticketno, employeeid, employee_name, assetpriority, asset_id, assetmodel, assettag,
                           assetserialno,
                           assetunit, service_request_type, None, additionalComments, "Open"]
            }

            status = base_object.asset_request_fulfillment(data_dict)

            if status:
                flash("Request Ticket No : {0}".format(ticketno), "success")
            else:
                flash("Failed to Create Asset Request", "danger")

        employee_id = base_object.get_employee_data([])
        request_priority = base_object.get_request_priority([])
        asset_details = base_object.get_asset_request([])
        del base_object

        return render_template('request_asset.html', username=session['username'], accountid=session['id'],
                               access_role=session['role'], access_role_status=session['status'],
                               employeeId=employee_id, requestPriority=request_priority, assetDetails=asset_details)

    elif request.method == "GET" and 'loggedin' in session and '2fa' in session and \
            (session['role'] in ['view', 'admin'] and session['status'] in ['approved', 'pending', 'reject']):

        base_object = BaseClass()
        employee_id = base_object.get_employee_data([])
        request_priority = base_object.get_request_priority([])
        asset_details = base_object.get_asset_request([])
        del base_object
        return render_template('request_asset.html', username=session['username'], accountid=session['id'],
                               access_role=session['role'], access_role_status=session['status'],
                               employeeId=employee_id, requestPriority=request_priority, assetDetails=asset_details)
    else:
        return render_template("404.html")


@app.route('/asset_retirement', methods=["POST", "GET"])
def asset_retirement():
    if request.method == "POST" and 'loggedin' in session and '2fa' in session and \
            session['role'] == 'admin' and session['status'] == 'approved':

        # Form
        asset_serialno = request.form.get("serialno")
        asset_tag = request.form.get("assettag")
        asset_model = request.form.get("assetmodel")
        asset_assetstockroom_building = request.form.get("assetstockroom1")
        asset_harddrive_dispose_status = request.form.get("fav_language")
        disposaldate = request.form.get("disposaldate")

        if asset_harddrive_dispose_status == "Yes":
            asset_harddrive_dispose_status = True
        else:
            asset_harddrive_dispose_status = False

        base_object = BaseClass()
        datalist = [asset_serialno, asset_tag, asset_model, asset_assetstockroom_building]
        asset_data = base_object.get_asset_data_by_srn_tag(datalist)
        if len(asset_data) == 0:
            flash("Please Check the Asset Inventory and Select Records", "danger")
        else:
            stockroom_id = asset_data[0]['stockroom_id']
            data_dict = {
                "query1": [asset_serialno, asset_tag, asset_model, asset_harddrive_dispose_status,
                           stockroom_id, disposaldate],
                "query2": [asset_serialno, asset_tag, asset_model, stockroom_id, asset_assetstockroom_building]
            }
            status = base_object.asset_retirement_insert_delete(data_dict)

            if status:
                flash("Asset Successfully Retired", "success")
            else:
                flash("Please Check the Asset Inventory and Select Records", "danger")

        asset_data = base_object.get_asset_data([])
        del base_object
        return render_template('asset_retirement.html', username=session['username'], accountid=session['id'],
                               access_role=session['role'], access_role_status=session['status'],
                               assetData=asset_data)
    elif request.method == "GET" and 'loggedin' in session and '2fa' in session and \
            session['role'] == 'admin' and session['status'] == 'approved':
        base_object = BaseClass()
        asset_data = base_object.get_asset_data([])
        del base_object
        return render_template('asset_retirement.html', username=session['username'], accountid=session['id'],
                               access_role=session['role'], access_role_status=session['status'],
                               assetData=asset_data)
    elif request.method == "GET" and 'loggedin' in session and '2fa' in session and \
            (session['role'] == 'view' and session['status'] == 'approved') or \
            (session['role'] == 'admin' and session['status'] in ['reject', 'pending']):
        return render_template("insufficient_privileges.html")
    else:
        return render_template("404.html")


@app.route('/asset_tracking', methods=["GET"])
def asset_tracking():
    if request.method == "GET" and 'loggedin' in session and '2fa' in session and \
            (session['role'] in ['view', 'admin'] and session['status'] in ['approved', 'pending', 'reject']):
        base_object = BaseClass()
        asset_data = base_object.get_asset_data([])
        del base_object
        return render_template('asset_tracking.html', username=session['username'], accountid=session['id'],
                               access_role=session['role'], access_role_status=session['status'],
                               assetData=asset_data)
    else:
        return render_template("404.html")


@app.route('/update_stockroom', methods=["POST", "GET"])
def update_stockroom():
    if request.method == "POST" and 'loggedin' in session and '2fa' in session and \
            session['role'] == 'admin' and session['status'] == 'approved':
        data_dict = OrderedDict()
        base_object = BaseClass()
        security_control = base_object.get_Security_control([])

        # Form
        stroomid = request.form.get("stroomid")
        bname = request.form.get("bname")
        rno = request.form.get("rno")
        raddress = request.form.get("raddress")
        scstockroom = request.form.get("scstockroom")
        srmanager = request.form.get("srmanager")

        data_dict['stockroom_id'] = stroomid
        data_dict['building'] = bname
        data_dict['room_number'] = rno
        data_dict['address'] = raddress
        data_dict['security_control'] = scstockroom
        data_dict['stockroom_manager'] = srmanager

        update_stockroom_status = base_object.update_stockroom(data_dict, security_control)
        if update_stockroom_status:
            flash("Successfully Updated Record", "success")
        else:
            flash("Failed to Update Record", "danger")
        del base_object
        return render_template('update_stockroom.html', username=session['username'], accountid=session['id'],
                               access_role=session['role'], access_role_status=session['status'],
                               securityControl=security_control)
    elif request.method == "GET" and 'loggedin' in session and '2fa' in session and \
            session['role'] == 'admin' and session['status'] == 'approved':
        base_object = BaseClass()
        security_control = base_object.get_Security_control([])
        del base_object
        return render_template('update_stockroom.html', username=session['username'], accountid=session['id'],
                               access_role=session['role'], access_role_status=session['status'],
                               securityControl=security_control)
    elif request.method == "GET" and 'loggedin' in session and '2fa' in session and \
            (session['role'] == 'view' and session['status'] == 'approved') or \
            (session['role'] == 'admin' and session['status'] in ['reject', 'pending']):
        return render_template("insufficient_privileges.html")
    else:
        return render_template("404.html")


@app.route('/insert_stockroomdata', methods=["POST", "GET"])
def insert_stockroomdata():
    if request.method == "POST" and 'loggedin' in session and '2fa' in session and \
            session['role'] == 'admin' and session['status'] == 'approved':
        base_object = BaseClass()
        security_control = base_object.get_Security_control([])

        bname = request.form.get("bname")
        rno = request.form.get("rno")
        raddress = request.form.get("raddress")
        scstockroom = request.form.get("scstockroom")
        srmanager = request.form.get("srmanager")

        security_control_id = None
        for item in security_control:
            if item['security_control_type'] == scstockroom:
                security_control_id = item['stockroom_security_type_id']

        data_list = [bname, rno, raddress, scstockroom, srmanager, security_control_id]
        add_stockroom_status = base_object.add_new_stockroom_entry(data_list)
        del base_object
        if add_stockroom_status:
            flash("Successfully Inserted Record", "success")
        else:
            flash("Record Already Exist", "danger")
        return render_template('insert_stockroomdata.html', username=session['username'], accountid=session['id'],
                               access_role=session['role'], access_role_status=session['status'],
                               securityControl=security_control)
    elif request.method == "GET" and 'loggedin' in session and '2fa' in session and \
            session['role'] == 'admin' and session['status'] == 'approved':
        base_object = BaseClass()
        security_control = base_object.get_Security_control([])
        del base_object
        return render_template('insert_stockroomdata.html', username=session['username'], accountid=session['id'],
                               access_role=session['role'], access_role_status=session['status'],
                               securityControl=security_control)
    elif request.method == "GET" and 'loggedin' in session and '2fa' in session and \
            (session['role'] == 'view' and session['status'] == 'approved') or \
            (session['role'] == 'admin' and session['status'] in ['reject', 'pending']):
        return render_template("insufficient_privileges.html")
    else:
        return render_template("404.html")


@app.route('/stockroom', methods=["GET"])
def stockroom():
    if request.method == "GET" and 'loggedin' in session and '2fa' in session and \
            (session['role'] in ['view', 'admin'] and session['status'] in ['approved', 'pending', 'reject']):
        base_object = BaseClass()
        stockroomData = base_object.get_Stockroom_data([])
        del base_object
        return render_template('stockroom_management.html', username=session['username'], accountid=session['id'],
                               access_role=session['role'], access_role_status=session['status'],
                               stockroomData=stockroomData)
    else:
        return render_template("404.html")


@app.route('/support', methods=["POST", "GET"])
def support():
    if request.method == "POST" and 'loggedin' in session and '2fa' in session and \
            (session['role'] in ['view', 'admin'] and session['status'] in ['approved', 'pending', 'reject']):
        service_request_type = "Support_Request"
        base_object = BaseClass()

        # Form
        employeeid = request.form.get("employeeid")
        assetpriority = request.form.get("assetpriority")
        assetmodel = request.form.get("assetmodel")
        assettag = request.form.get("assettag")
        assetserialno = request.form.get("assetserialno")
        service_type = request.form.get("service_type")
        additionalComments = request.form.get("additionalComments")

        if additionalComments == "":
            additionalComments = None
        acceptassetterms = request.form.get("acceptassetterms")

        if acceptassetterms != "Yes":
            flash("Please Check the Terms and Condition !", "danger")
        else:

            ticketno = base_object.get_max_support_ticket_no([])
            if ticketno == None:
                ticketno = 1000001

            user_data = base_object.get_employee_data_id([employeeid])
            employee_name = user_data[0]['first_name']

            asset_priority_data = base_object.get_request_priority_id([assetpriority])
            asset_priority_id = asset_priority_data[0]['id']

            asset_data = base_object.get_asset_data_by_srn_tag_model([assetserialno, assettag, assetmodel])
            asset_id = asset_data[0]['asset_id']

            data_dict = {
                "query1": [ticketno, employeeid, employee_name, assetpriority, asset_priority_id, asset_id, assetmodel,
                           assettag, assetserialno, service_type, additionalComments
                           ],
                "query2": [ticketno, employeeid, employee_name, assetpriority, asset_id, assetmodel, assettag,
                           assetserialno,
                           None, service_request_type, service_type, additionalComments, "Open"]
            }

            status = base_object.asset_support_fulfillment(data_dict)

            if status:
                flash("Support Ticket No : {0}".format(ticketno), "success")
            else:
                flash("Failed to Create Support Request", "danger")

        employee_id = base_object.get_employee_data([])
        request_priority = base_object.get_request_priority([])
        asset_details = base_object.get_asset_request_all([])
        del base_object

        return render_template('support.html', username=session['username'], accountid=session['id'],
                               access_role=session['role'], access_role_status=session['status'],
                               employeeId=employee_id, requestPriority=request_priority, assetDetails=asset_details)

    elif request.method == "GET" and 'loggedin' in session and '2fa' in session and \
            (session['role'] in ['view', 'admin'] and session['status'] in ['approved', 'pending', 'reject']):

        base_object = BaseClass()
        employee_id = base_object.get_employee_data([])
        request_priority = base_object.get_request_priority([])
        asset_details = base_object.get_asset_request_all([])
        del base_object
        return render_template('support.html', username=session['username'], accountid=session['id'],
                               access_role=session['role'], access_role_status=session['status'],
                               employeeId=employee_id, requestPriority=request_priority, assetDetails=asset_details)
    else:
        return render_template("404.html")


@app.route('/requests_fulfillment', methods=["GET"])
def requests_fulfillment():
    if request.method == "GET" and 'loggedin' in session and '2fa' in session and \
            session['role'] == 'admin' and session['status'] == 'approved':
        base_object = BaseClass()
        requestfulfillmentdata = base_object.get_request_fulfillment_data([])
        del base_object
        return render_template('requests_fulfillment.html', username=session['username'], accountid=session['id'],
                               access_role=session['role'], access_role_status=session['status'],
                               requestFulfillmentData=requestfulfillmentdata)
    elif request.method == "GET" and 'loggedin' in session and '2fa' in session and \
            (session['role'] == 'view' and session['status'] == 'approved') or \
            (session['role'] == 'admin' and session['status'] in ['reject', 'pending']):
        return render_template("insufficient_privileges.html")
    else:
        return render_template("404.html")


@app.route('/requests_fulfillment_process', methods=["POST", "GET"])
def requests_fulfillment_process():
    if request.method == "POST" and 'loggedin' in session and '2fa' in session and \
            session['role'] == 'admin' and session['status'] == 'approved':

        base_object = BaseClass()

        # Form
        tno = request.form.get("tno")
        eid = request.form.get("eid")
        ename = request.form.get("ename")
        trequest_type = request.form.get("trequest_type")
        tstatus = request.form.get("tstatus")

        if trequest_type == "Asset_Request" and tstatus == "Done":
            # logging_client = logging.Client()
            # logging_client.setup_logging()
            # log.error(f"Inside request: Inside request")
            requestfulfillmentdata = base_object.get_request_fulfillment_by_ticketno([tno])
            asset_id = requestfulfillmentdata[0]['asset_id']
            data_dict = {
                "query1": [ename, eid, asset_id],
                "query2": [tstatus, tno]
            }
            status = base_object.update_asset_fulfillment(data_dict)

            if status:
                flash("Request is Successfully Fulfilled", "success")
            else:
                flash("Failed to Fulfill request", "danger")
            requestfulfillmentdata = base_object.get_request_fulfillment_data([])
            del base_object
            return render_template('requests_fulfillment.html', username=session['username'], accountid=session['id'],
                                   access_role=session['role'], access_role_status=session['status'],
                                   requestFulfillmentData=requestfulfillmentdata)

        elif trequest_type == "Support_Request" and tstatus == "Done":
            data_list = [tstatus, tno]
            status = base_object.update_asset_fulfillment_process(data_list)
            if status:
                flash("Request is Successfully Fulfilled", "success")
            else:
                flash("Failed to Fulfill request", "danger")
            requestfulfillmentdata = base_object.get_request_fulfillment_data([])
            del base_object
            return render_template('requests_fulfillment.html', username=session['username'], accountid=session['id'],
                                   access_role=session['role'], access_role_status=session['status'],
                                   requestFulfillmentData=requestfulfillmentdata)
        elif tstatus == "Backlog":
            data_list = [tstatus, tno]
            status = base_object.update_asset_fulfillment_process(data_list)
            if status:
                flash("Request is set to {}".format(tstatus), "success")
            else:
                flash("Failed to Fulfill request", "danger")
            requestfulfillmentdata = base_object.get_request_fulfillment_data([])
            del base_object
            return render_template('requests_fulfillment.html', username=session['username'], accountid=session['id'],
                                   access_role=session['role'], access_role_status=session['status'],
                                   requestFulfillmentData=requestfulfillmentdata)
        elif tstatus == "Open":
            data_list = [tstatus, tno]
            status = base_object.update_asset_fulfillment_process(data_list)
            if status:
                flash("Request is set to {}".format(tstatus), "success")
            else:
                flash("Failed to Fulfill request", "danger")
            requestfulfillmentdata = base_object.get_request_fulfillment_data([])
            del base_object
            return render_template('requests_fulfillment.html', username=session['username'], accountid=session['id'],
                                   access_role=session['role'], access_role_status=session['status'],
                                   requestFulfillmentData=requestfulfillmentdata)
        else:
            flash("Please review the Request and Change the State", "danger")
            del base_object
            return render_template('requests_fulfillment_process.html', username=session['username'],
                                   accountid=session['id'])
    if request.method == "GET" and 'loggedin' in session and '2fa' in session and \
            session['role'] == 'admin' and session['status'] == 'approved':
        return render_template('requests_fulfillment_process.html', username=session['username'],
                               accountid=session['id'],access_role=session['role'], access_role_status=session['status'])
    elif request.method == "GET" and 'loggedin' in session and '2fa' in session and \
            (session['role'] == 'view' and session['status'] == 'approved') or \
            (session['role'] == 'admin' and session['status'] in ['reject', 'pending']):
        return render_template("insufficient_privileges.html")
    else:
        return render_template("404.html")


@app.route('/user_roles', methods=["POST", "GET"])
def user_roles():
    if request.method == "POST" and 'loggedin' in session and '2fa' in session and \
            session['role'] == 'admin' and session['status'] == 'approved':

        # Form
        eid = request.form.get("eid")
        rbacstatus = request.form.get("rbacstatus")
        base_object = BaseClass()

        if eid not in ("", None):
            data_list = [rbacstatus, eid]
            status = base_object.update_user_roles(data_list)
            if status:
                flash("Roles has been sucessfully Updated", "success")
            else:
                flash("Failed to Update Role", "danger")
        else:
            flash("Please Select Employee ID", "danger")

        emp_data = base_object.get_user_roles_data([])
        del base_object
        return render_template('user_roles.html', username=session['username'], accountid=session['id'],
                               access_role=session['role'], access_role_status=session['status'],
                               empData=emp_data)
    elif request.method == "GET" and 'loggedin' in session and '2fa' in session and \
            session['role'] == 'admin' and session['status'] == 'approved':
        base_object = BaseClass()
        emp_data = base_object.get_user_roles_data([])
        del base_object
        return render_template('user_roles.html', username=session['username'], accountid=session['id'],
                               access_role=session['role'], access_role_status=session['status'],
                               empData=emp_data)
    elif request.method == "GET" and 'loggedin' in session and '2fa' in session and \
            (session['role'] == 'view' and session['status'] == 'approved') or \
            (session['role'] == 'admin' and session['status'] in ['reject', 'pending']):
        return render_template("insufficient_privileges.html")
    else:
        return render_template("404.html")


@app.route('/user_setting', methods=["GET"])
def user_setting():
    if request.method == "GET" and 'loggedin' in session and '2fa' in session and \
            (session['role'] in ['view', 'admin'] and session['status'] in ['approved', 'pending', 'reject']):
        base_object = BaseClass()
        user_name = session['username']
        account_id = session['id']
        user_data = base_object.get_user_data([user_name, account_id])
        del base_object
        return render_template('user_setting.html', username=session['username'], accountid=session['id'],
                               access_role=session['role'], access_role_status=session['status'],
                               userData=user_data[0])
    else:
        return render_template("404.html")


@app.route('/change_first_name', methods=["POST", "GET"])
def change_first_name():
    if request.method == "POST" and 'loggedin' in session and '2fa' in session and \
            (session['role'] in ['view', 'admin'] and session['status'] in ['approved', 'pending', 'reject']):
        # Form
        firstname = request.form.get("firstname")
        base_object = BaseClass()
        account_id = session['id']
        update_status = base_object.update_firstname([firstname, account_id])
        del base_object
        if update_status:
            session['username'] = firstname
            flash("Successfully updated First Name", "success")
            return redirect(url_for('user_setting'))
        else:
            flash("Failed to Update Firstname !", "danger")
            return render_template('change_first_name.html', username=session['username'], accountid=session['id'],
                                   access_role=session['role'], access_role_status=session['status'])
    elif request.method == "GET" and 'loggedin' in session and '2fa' in session and \
            (session['role'] in ['view', 'admin'] and session['status'] in ['approved', 'pending', 'reject']):
        return render_template('change_first_name.html', username=session['username'], accountid=session['id'],
                               access_role=session['role'], access_role_status=session['status'])
    else:
        return render_template("404.html")


@app.route('/change_middle_name', methods=["POST", "GET"])
def change_middle_name():
    if request.method == "POST" and 'loggedin' in session and '2fa' in session and \
            (session['role'] in ['view', 'admin'] and session['status'] in ['approved', 'pending', 'reject']):
        # Form
        middlename = request.form.get("middlename")
        base_object = BaseClass()
        account_id = session['id']
        update_status = base_object.update_middlename([middlename, account_id])
        del base_object
        if update_status:
            flash("Successfully updated Middle Name", "success")
            return redirect(url_for('user_setting'))
        else:
            flash("Failed to Update Middle Name !", "danger")
            return render_template('change_middle_name.html', username=session['username'], accountid=session['id'],
                                   access_role=session['role'], access_role_status=session['status'])
    elif request.method == "GET" and 'loggedin' in session and '2fa' in session and \
            (session['role'] in ['view', 'admin'] and session['status'] in ['approved', 'pending', 'reject']):
        return render_template('change_middle_name.html', username=session['username'], accountid=session['id'],
                               access_role=session['role'], access_role_status=session['status'])
    else:
        return render_template("404.html")


@app.route('/change_last_name', methods=["POST", "GET"])
def change_last_name():
    if request.method == "POST" and 'loggedin' in session and '2fa' in session and \
            (session['role'] in ['view', 'admin'] and session['status'] in ['approved', 'pending', 'reject']):
        # Form
        lastname = request.form.get("lastname")
        base_object = BaseClass()
        account_id = session['id']
        update_status = base_object.update_lastname([lastname, account_id])
        del base_object
        if update_status:
            flash("Successfully updated Last Name", "success")
            return redirect(url_for('user_setting'))
        else:
            flash("Failed to Update Last Name !", "danger")
            return render_template('change_last_name.html', username=session['username'], accountid=session['id'],
                                   access_role=session['role'], access_role_status=session['status'])
    elif request.method == "GET" and 'loggedin' in session and '2fa' in session and \
            (session['role'] in ['view', 'admin'] and session['status'] in ['approved', 'pending', 'reject']):
        return render_template('change_last_name.html', username=session['username'], accountid=session['id'],
                               access_role=session['role'], access_role_status=session['status'])
    else:
        return render_template("404.html")


@app.route('/change_birthdate', methods=["POST", "GET"])
def change_birthdate():
    if request.method == "POST" and 'loggedin' in session and '2fa' in session and \
            (session['role'] in ['view', 'admin'] and session['status'] in ['approved', 'pending', 'reject']):
        # Form
        birthday = request.form.get("birthday")
        base_object = BaseClass()
        account_id = session['id']
        update_status = base_object.change_birthdate([birthday, account_id])
        del base_object
        if update_status:
            flash("Successfully updated Birthdate", "success")
            return redirect(url_for('user_setting'))
        else:
            flash("Failed to Update Birthdate !", "danger")
            return render_template('change_birthdate.html', username=session['username'], accountid=session['id'],
                                   access_role=session['role'], access_role_status=session['status'])
    elif request.method == "GET" and 'loggedin' in session and '2fa' in session and \
            (session['role'] in ['view', 'admin'] and session['status'] in ['approved', 'pending', 'reject']):
        return render_template('change_birthdate.html', username=session['username'], accountid=session['id'],
                               access_role=session['role'], access_role_status=session['status'])
    else:
        return render_template("404.html")


@app.route('/change_email_address', methods=["POST", "GET"])
def change_email_address():
    if request.method == "POST" and 'loggedin' in session and '2fa' in session and \
            (session['role'] in ['view', 'admin'] and session['status'] in ['approved', 'pending', 'reject']):
        # Form
        emailid = request.form.get("emailid")

        base_object = BaseClass()

        # get userdata
        username = session['username']
        accountid = session['id']
        user_data = base_object.get_user_data([username, accountid])
        email_address = user_data[0]['email_address']

        # check email is already taken
        data_list = [emailid.lower()]
        email_status = base_object.check_email_exist(data_list)

        if email_address == emailid:
            flash("Please Don't use old Email Id !", "danger")
        elif email_status:
            flash("Email address is already Taken !", "danger")
        else:
            update_status = base_object.change_email_address([emailid, accountid])
            if update_status:
                flash("Successfully updated Email Address", "success")
                return redirect(url_for('user_setting'))
            else:
                flash("Failed to Update Email Address !", "danger")

        del base_object
        return render_template('change_email_address.html', username=session['username'], accountid=session['id'],
                               access_role=session['role'], access_role_status=session['status'])
    elif request.method == "GET" and 'loggedin' in session and '2fa' in session and \
            (session['role'] in ['view', 'admin'] and session['status'] in ['approved', 'pending', 'reject']):
        return render_template('change_email_address.html', username=session['username'], accountid=session['id'],
                               access_role=session['role'], access_role_status=session['status'])
    else:
        return render_template("404.html")


@app.route('/change_contact_number', methods=["POST", "GET"])
def change_contact_number():
    if request.method == "POST" and 'loggedin' in session and '2fa' in session and \
            (session['role'] in ['view', 'admin'] and session['status'] in ['approved', 'pending', 'reject']):
        # Form
        typePhone = request.form.get("typePhone")
        base_object = BaseClass()
        account_id = session['id']
        update_status = base_object.change_contact_number([typePhone, account_id])
        del base_object
        if update_status:
            flash("Successfully updated Contact Number", "success")
            return redirect(url_for('user_setting'))
        else:
            flash("Failed to Update Contact Number !", "danger")
            return render_template('change_contact_number.html', username=session['username'], accountid=session['id'],
                                   access_role=session['role'], access_role_status=session['status'])
    elif request.method == "GET" and 'loggedin' in session and '2fa' in session and \
            (session['role'] in ['view', 'admin'] and session['status'] in ['approved', 'pending', 'reject']):
        return render_template('change_contact_number.html', username=session['username'], accountid=session['id'],
                               access_role=session['role'], access_role_status=session['status'])
    else:
        return render_template("404.html")


@app.route('/change_privilege', methods=["POST", "GET"])
def change_privilege():
    if request.method == "POST" and 'loggedin' in session and '2fa' in session and \
            (session['role'] in ['view', 'admin'] and session['status'] in ['approved', 'pending', 'reject']):
        # Form
        changepriv = request.form.get("changepriv")

        base_object = BaseClass()
        username = session['username']
        accountid = session['id']
        user_data = base_object.get_user_data([username, accountid])
        user_role = user_data[0]['role']
        print(changepriv, user_role)
        if user_role != changepriv:
            status = base_object.change_user_role([changepriv, accountid])
            if status:
                flash("Sucessfully sent Request to Admin for Approval", "success")
            else:
                flash("Failed to Sent request to Admin for Approval", "danger")
        else:
            flash("Please Don't request Same Role", "danger")

        del base_object
        return render_template('change_privilege.html', username=session['username'], accountid=session['id'],
                               access_role=session['role'], access_role_status=session['status'],
                               userData=user_data[0])

    elif request.method == "GET" and 'loggedin' in session and '2fa' in session and \
            (session['role'] in ['view', 'admin'] and session['status'] in ['approved', 'pending', 'reject']):
        base_object = BaseClass()
        username = session['username']
        accountid = session['id']
        user_data = base_object.get_user_data([username, accountid])
        del base_object
        return render_template('change_privilege.html', username=session['username'], accountid=session['id'],
                               access_role=session['role'], access_role_status=session['status'], userData=user_data[0]
                               )
    else:
        return render_template("404.html")


@app.route('/change_qr', methods=["GET"])
def change_qr():
    if request.method == "GET" and 'loggedin' in session and '2fa' in session and \
            (session['role'] in ['view', 'admin'] and session['status'] in ['approved', 'pending', 'reject']):

        base_object = BaseClass()

        # get userdata
        username = session['username']
        accountid = session['id']
        user_data = base_object.get_user_data([username, accountid])
        email_address = user_data[0]['email_address']

        secret = pyotp.random_base32()
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(email_address, issuer_name=PROJECT.PROJECT_NAME)
        qr_code = qrcode.make(totp_uri)
        qr_data = io.BytesIO()
        qr_code.save(qr_data, "PNG")
        qr_code_binary = qr_data.getvalue()

        status = base_object.change_user_qr_code([secret, qr_code_binary, accountid, email_address])
        if status:
            flash("Sucessfully Generated New 2FA", "success")
        else:
            flash("Failed to Generate New 2FA", "danger")

        user_data = base_object.get_user_data([username, accountid])
        secret_key = user_data[0]['otp_encoder']
        qr_code = user_data[0]['qr_code']
        decoded_qr_code = b64encode(qr_code).decode("utf-8")

        del base_object

        return render_template('change_qr.html', username=session['username'], accountid=session['id'],
                               access_role=session['role'], access_role_status=session['status'], secret=secret_key,
                               image=decoded_qr_code)
    else:
        return render_template("404.html")


@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if request.method == "POST" and 'loggedin' in session and '2fa' in session and \
            (session['role'] in ['view', 'admin'] and session['status'] in ['approved', 'pending', 'reject']):

        # form
        inputPassword = request.form.get("inputPassword1")
        inputPasswordConfirm = request.form.get("inputPasswordConfirm1")


        base_object = BaseClass()

        # get userdata
        username = session['username']
        accountid = session['id']
        user_data = base_object.get_user_data([username, accountid])
        email_address = user_data[0]['email_address']
        old_password = user_data[0]['password']

        # check terms and condition checkbox
        if not request.form.get('forgetpswterms'):
            flash("Please Accept the Terms and Condition !", "danger")
            return render_template('change_password.html', username=session['username'], accountid=session['id'],
                                   access_role=session['role'], access_role_status=session['status'])

        # updating password
        if inputPassword != inputPasswordConfirm:
            flash("Passwords does not match !", "danger")
            return render_template('change_password.html', username=session['username'], accountid=session['id'],
                                   access_role=session['role'], access_role_status=session['status'])

        if old_password == inputPasswordConfirm:
            flash("Old Password is Same !", "danger")
            return render_template('change_password.html', username=session['username'], accountid=session['id'],
                                   access_role=session['role'], access_role_status=session['status'])
        else:
            data_list = [inputPasswordConfirm, email_address]
            update_status = base_object.update_password(data_list)
            del base_object
            if update_status:
                session.clear()
                return redirect(url_for('login'))
            else:
                flash("Failed to Update the password !", "danger")
                return render_template('change_password.html', username=session['username'], accountid=session['id'],
                                       access_role=session['role'], access_role_status=session['status'])

    elif request.method == "GET" and 'loggedin' in session and '2fa' in session and \
             (session['role'] in ['view', 'admin'] and session['status'] in ['approved', 'pending', 'reject']):
        return render_template('change_password.html', username=session['username'], accountid=session['id'],
                               access_role=session['role'], access_role_status=session['status']
                               )
    else:
        return render_template("404.html")


@app.route('/activity_log', methods=['GET'])
def activity_log():
    if request.method == "GET" and 'loggedin' in session and '2fa' in session and \
            (session['role'] in ['view', 'admin'] and session['status'] in ['approved', 'pending', 'reject']):
        base_object = BaseClass()
        username = session['username']
        accountid = session['id']
        requestfulfillmentdata = base_object.get_request_fulfillment_data_by_employee_id([accountid, username])
        del base_object
        return render_template('activity_log.html', username=session['username'], accountid=session['id'],
                               access_role=session['role'], access_role_status=session['status'],
                               requestFulfillmentData=requestfulfillmentdata)
    else:
        return render_template("404.html")

if __name__ == "__main__":
    # client = secretmanager.SecretManagerServiceClient()
    # name = f"projects/anil-research/secrets/itam/versions/latest"
    # response = client.access_secret_version(request={"name": name})
    # payload = response.payload.data.decode("UTF-8")
    # secret_manager = json.loads(payload)
    # print("printing secret",secret_manager)

    # DATABASE.USERNAME = secret_manager['USERNAME']
    # DATABASE.PASSWORD = secret_manager['PASSWORD']
    # DATABASE.HOST = secret_manager['HOST']
    # DATABASE.PORT = secret_manager['PORT']
    # DATABASE.CHARSET = secret_manager['CHARSET']
    # DATABASE.AUTOCOMMIT = secret_manager['AUTOCOMMIT']
    # DATABASE.DATABASE = secret_manager['DATABASE']
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
