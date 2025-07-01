import os
import csv
import secrets
from flask import Flask, request, abort, Response, render_template, CORS
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__)
auth = HTTPBasicAuth()
root_dir = os.getcwd()
reserved_names = ['new', 'echo']
app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app)#, resources={r"/<client>/<collection>": {"origins": "*"}, r"/echo": {"origins": "*"}})

@auth.verify_password
def verify_password(username, password):
    if username == "":
        return None
    
    if os.path.exists(f"{root_dir}/{username}/.passwd"):
        with open(f"{root_dir}/{username}/.passwd", 'r') as users:
            for line in users.readlines():
                user, passwd = line.split(':', 2)
                if username.lower() == user:
                    if password == passwd:
                        return user
                    else:
                        return None
    return None

@auth.get_user_roles
def get_user_roles(username):
    print(username)
    if os.path.exists(f"{root_dir}/users.txt"):
        with open(f"{root_dir}/users.txt", 'r') as users:
            for line in users.readlines():
                user, _, groups = line.split(':', 3)
                if username.lower() == user:
                    return groups.split(',')
    return []

@app.route("/new", methods=['GET'])
def index():
    return render_template('new.html', error="")

@app.route("/new", methods=['POST'])
def create_client():
    client = request.form["client"].lower()
    if client == "":
        return render_template('new.html', error="Please fill out.")
    elif '.' in client:
        return render_template('new.html', error="Invalid characters")
    elif os.path.exists(f"{root_dir}/{client}/") or client in reserved_names:
        return render_template('new.html', error="Already exists.")
    else:
        passwd = secrets.token_urlsafe(8)
        os.mkdir(f"{root_dir}/{client}/")
        with open(f"{root_dir}/{client}/.passwd", mode='w') as pwfile:
            pwfile.write(f"{client}:{passwd}")
        return render_template('new_success.html', client=client, passwd=passwd)


@app.route("/<client>", methods=['GET'])
@auth.login_required
def list_collections(client):
    if auth.current_user() == client:
        if os.path.exists(f"{root_dir}/{client}/"):
            return render_template('collections.html', client=client, collections=[f[0:-4] for f in os.listdir(f"{root_dir}/{client}/") if f.endswith(".csv")])
        else:
            return abort(404)
    else:
        return abort(401)

@app.route("/<client>/<collection>", methods=['GET'])
@auth.login_required
def get_collection(client, collection):
    if auth.current_user() == client:
        if os.path.exists(f"{root_dir}/{client}/{collection}.csv"):
            with open(f"{root_dir}/{client}/{collection}.csv", 'r') as csvfile:
                return Response(csvfile.read(), mimetype='text/csv')
        else:
            abort(404)
    else:
        abort(401)

@app.route("/echo", methods=['POST'])
def post_test():
    return request.form

@app.route("/<client>/<collection>", methods=['POST'])
def post_data(client, collection):
    if os.path.exists(f"{root_dir}/{client}/") == False:
        abort(404)

    csv_path = f"{root_dir}/{client}/{collection}.csv"
    if os.path.exists(csv_path):
        headers = []
        with open(csv_path, 'r') as csvfile:
            reader = csv.reader(csvfile)
            headers = next(reader)
        
        with open(csv_path, mode='a') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow([request.form[f] if f in request.form.keys() else '' for f in headers])
    else:
        with open(csv_path, mode='w') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(request.form.keys())
            writer.writerow(request.form.values())
    
    return ('', 204)
