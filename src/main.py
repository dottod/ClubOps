from flask import Flask, request, render_template, jsonify, redirect
from datetime import datetime
import dbinit as dbfunctions
from sqlalchemy import create_engine
import pymysql

request_count = 0
requests_registered = []

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def redirect_home():
    return redirect('/home')

@app.route('/home', methods=['GET', 'POST'])
def home():
    with open('metafile.json', 'r') as file:
        file_data = json.load(file)

    selected_type = request.form.get('type', None)
    number_of_keys = len(request.form.keys())

    if number_of_keys == 1:
        return render_template('home.html', number_of_requests=request_count, all_types=file_data.keys(),
                               selected_type=selected_type, selected_type_fields=file_data.get(selected_type, None),
                               number_of_keys=number_of_keys)
    elif number_of_keys == 0:
        return render_template('home.html', number_of_requests=request_count, all_types=file_data.keys(),
                               selected_type=selected_type, selected_type_fields=[] if selected_type is None else file_data.get(selected_type, []),
                               number_of_keys=number_of_keys)
    else:
        resultant()
        return redirect('/status')

def resultant():
    global request_count
    global requests_registered
    returned_data = (True, 'Invalid.')

    data = dict(request.form)

    if data is None:
        return render_template('status.html')

    try:
        connection_string = '''mysql+pymysql://{userName}:{password}@{serverName}'''.format(
            serverName=data['serverName'], userName=data['userName'], password=data['password'])
        ssl_args = {'ssl_ca': 'key.crt.pem'}
        engine = create_engine(connection_string, connect_args=ssl_args)

        with engine.connect() as con:
            con.execute('select 1')

    except Exception as e:
        returned_data = (False, 'Invalid credentials: ' + str(e))
        request_count += 1
        requests_registered.append((request_count, datetime.now().strftime("%Y/%d/%m %H:%M:%S"), data,
                                    returned_data[0], returned_data[1]))
        return None

    try:
        request_type = data['type'].lower().strip()

        if request_type == 'replicate':
            returned_data = dbfunctions.replicate_schema(engine, data)
        elif request_type == 'change_live_systems':
            returned_data = dbfunctions.change_all_live(data)
        elif request_type == 'update_file':
            returned_data = dbfunctions.create_child(engine, data)
        elif request_type == 'show_metadata':
            returned_data = dbfunctions.show_metadata_json()
        elif request_type == 'add_metadata':
            returned_data = dbfunctions.add_metadata_json(data)
        elif request_type == 'delete_metadata':
            returned_data = dbfunctions.delete_metadata_json(data)
        elif request_type == 'initialize':
            returned_data = dbfunctions.apply_changes(data)
        elif request_type == 'create_script':
            returned_data = dbfunctions.writeSQLScript(dbfunctions.propagatechanges(data['fileName'], data, True))

    except Exception as e:
        returned_data = (False, str(e))

    request_count += 1
    requests_registered.append((request_count, datetime.now().strftime("%Y/%d/%m %H:%M:%S"), data,
                                returned_data[0], returned_data[1]))

    return None

@app.route('/status', methods=['GET', 'POST'])
def result():
    global requests_registered
    global request_count

    new_requests = requests_registered.copy()
    new_requests.reverse()

    return render_template('status.html', items=new_requests)

if __name__ == '__main__':
    app.run(debug=True)
