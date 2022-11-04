from flask import Flask, render_template
import os

app = Flask(__name__)


@app.route('/')
@app.route('/login')
def login():
    return render_template('login.html')
    # return 'helloworld'


@app.route('/forget_password')
def forget_password():
    return render_template('forget_password.html')
    # return 'helloworld'


@app.route('/registration')
def registration():
    return render_template('register.html')
    # return 'helloworld'


@app.route('/home_page')
def home_page():
    return render_template('index.html')
    # return 'helloworld'


@app.route('/add_asset')
def add_asset():
    return render_template('add_asset.html')
    # return 'helloworld'


@app.route('/request_asset')
def request_asset():
    return render_template('request_asset.html')
    # return 'helloworld'


@app.route('/asset_retirement')
def asset_retirement():
    return render_template('asset_retirement.html')
    # return 'helloworld'


@app.route('/stockroom')
def stockroom():
    return render_template('stockroom_management.html')
    # return 'helloworld'


@app.route('/asset_tracking')
def asset_tracking():
    return render_template('asset_tracking.html')
    # return 'helloworld'


@app.route('/update_stockroom')
def update_stockroom():
    return render_template('update_stockroom.html')
    # return 'helloworld'


@app.route('/insert_stockroomdata')
def insert_stockroomdata():
    return render_template('insert_stockroomdata.html')
    # return 'helloworld'


@app.route('/support')
def support():
    return render_template('support.html')
    # return 'helloworld'


@app.route('/requests_fulfillment')
def requests_fulfillment():
    return render_template('requests_fulfillment.html')
    # return 'helloworld'

@app.route('/requests_fulfillment_process')
def requests_fulfillment_process():
    return render_template('requests_fulfillment_process.html')
    # return 'helloworld'

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
