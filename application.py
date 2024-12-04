import os
import csv
from flask import Flask, request, abort, Response
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__)
auth = HTTPBasicAuth()
root_dir = os.getcwd()

@auth.verify_password
def verify_password(username, password):
    if os.path.exists(f"{root_dir}/users.txt"):
        with open(f"{root_dir}/users.txt", 'r') as users:
            for line in users.readlines():
                print(line)
                user, passwd, _ = line.split(':', 3)
                if username == user:
                    if password == passwd:
                        return user
                    else:
                        return None
    return None

@auth.get_user_roles
def get_user_roles(username):
    if os.path.exists(f"{root_dir}/users.txt"):
        with open(f"{root_dir}/users.txt", 'r') as users:
            for line in users.readlines():
                user, _, groups = line.split(':', 3)
                if username == user:
                    print(groups.split(','))
                    return groups.split(',')

def check_access(client)->bool:
    return "admin" in get_user_roles(auth.current_user()) or auth.current_user() == client

@app.route("/<client>", methods=['GET'])
@auth.login_required
def list_collections(client):
    if check_access(client):
        if os.path.exists(f"{root_dir}/{client}/"):
            return os.listdir(f"{root_dir}/{client}/")
        else:
            return abort(404)
    else:
        return abort(401)

@app.route("/<client>/<collection>", methods=['GET'])
@auth.login_required
def get_collection(client, collection):
    if check_access(client):
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