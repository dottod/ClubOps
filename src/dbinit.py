import os
import json
from sqlalchemy import create_engine
import pandas as pd
import DBObject as db

ROOT_FOLDER_NAME = 'MySQL_DBSetup'
BASE_DIR = str(os.getcwd())[:os.getcwd().index(ROOT_FOLDER_NAME) + len(ROOT_FOLDER_NAME)]
GENERIC_CLUB_NAME = '@_@_@'
METADATA_FILE_NAME = 'metadata.json'


def get_schema_names(query):
    '''
    Returns all the schema names referred in a query.
    '''
    final_list = []
    query = query.lower().strip()
    tables = get_table_names(query)
    for table in tables:
        if '.' in table:
            schema, table = table.split('.')
            if schema not in final_list:
                final_list.append(schema)
    return final_list


def get_table_names(query):
    '''
    Returns all the referred table names in views and stored procedures.
    '''
    table_names = {}
    query = query.replace('(', ' ').replace(')', ' ').replace('\n', ' ').replace(';', ' ').replace('`', '').lower()
    tokenized_query = query.split(' ')
    tokenized_query = list(filter(None, tokenized_query))
    for index, token in enumerate(tokenized_query):
        if (token == 'from' or token == 'join') and len(tokenized_query[index + 1]) > 0:
            if tokenized_query[index + 1] != 'select':
                table_names[tokenized_query[index + 1]] = 1
    return list(table_names.keys())


def get_new_definition(engine, data):
    '''
    Returns the new definition of the requested data object, which can be a table, view, or stored procedure.
    '''
    try:
        new_definition = ''
        data['objectType'] = data['objectType'].capitalize().strip()
        query = 'SHOW CREATE {objectType} {schemaName}.{objectName};'.format(
            schemaName=data['schemaName'], objectName=data['objectName'], objectType=data['objectType'])
        with engine.connect().execution_options(autocommit=True) as con:
            rs = con.execute(query)

        df = pd.DataFrame(rs.fetchall(), columns=rs.keys())
        new_definition = df['Create {objectType}'.format(objectType=data['objectType'])].iloc[0]

        with open(os.path.join(BASE_DIR, data['serverName'], METADATA_FILE_NAME), 'r') as file:
            metafile = json.load(file)

        projectName = metafile[data['schemaName']]['projectName']
        indicator = metafile[data['schemaName']]['indicator']
        similarClub = data['schemaName']

        all_schema_names = {}
        for key, value in metafile.items():
            if value['projectName'] == projectName and key.replace(value['indicator'], '') == similarClub.replace(indicator, ''):
                all_schema_names[key] = value['indicator']

        if data['objectType'] == 'Table':
            new_definition = 'CREATE DATABASE IF NOT EXISTS {schemaName};\nUSE {schemaName};\n'.format(
                schemaName=data['schemaName']) + new_definition
            placeholder = new_definition.index('TABLE') + 5
            new_definition = new_definition[:placeholder] + ' IF NOT EXISTS ' + new_definition[placeholder:]
        elif data['objectType'] == 'Procedure':
            new_definition = 'CREATE ' + new_definition[new_definition.index('PROCEDURE'):]
            new_definition = 'CREATE DATABASE IF NOT EXISTS {schemaName};\nUSE {schemaName};\n'.format(
                schemaName=data['schemaName']) + '\nDROP PROCEDURE IF EXISTS {procedureName};\n'.format(
                procedureName=data['objectName']) + new_definition
            placeholder = new_definition.index('PROCEDURE') + 9
            new_definition = new_definition[:placeholder] + ' IF NOT EXISTS ' + new_definition[placeholder:]
            new_definition = new_definition.replace(data['schemaName'] + '.', '')
            for key, value in all_schema_names.items():
                new_definition = new_definition.replace(key + '.', '')

        elif data['objectType'] == 'View':
            new_definition = 'CREATE ' + new_definition[new_definition.index('VIEW'):]
            new_definition = 'CREATE DATABASE IF NOT EXISTS {schemaName};\nUSE {schemaName};\n'.format(
                schemaName=data['schemaName']) + '\nDROP VIEW IF EXISTS {viewName};\n'.format(
                viewName=data['objectName']) + new_definition
            placeholder = new_definition.index('VIEW') + 4
            new_definition = new_definition[:placeholder] + ' IF NOT EXISTS ' + new_definition[placeholder:]
            new_definition = new_definition.replace(data['schemaName'] + '.', '')
            for key, value in all_schema_names.items():
                new_definition = new_definition.replace(key + '.', '')
                new_definition = new_definition.replace(key + '@_@_@', value + '@_@_@')

        return new_definition

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None


def generate_metadata_file(server_name, schema_name, project_name, indicator):
    '''
    Generates the metadata file for the specified server, schema, project, and indicator.
    '''
    metadata = {}
    metadata[schema_name] = {'projectName': project_name, 'indicator': indicator}
    with open(os.path.join(BASE_DIR, server_name, METADATA_FILE_NAME), 'w') as file:
        json.dump(metadata, file)


def main():
    # Get the database credentials and connection details
    db_config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'username',
        'password': 'password'
    }

    # Create the SQLAlchemy engine
    engine = create_engine(f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/")

    # Get the list of schema names from the database
    with engine.connect().execution_options(autocommit=True) as con:
        rs = con.execute('SHOW DATABASES')
        schema_names = [row[0] for row in rs]

    # Iterate over the schema names
    for schema_name in schema_names:
        # Create a directory for the server if it doesn't exist
        server_dir = os.path.join(BASE_DIR, schema_name)
        os.makedirs(server_dir, exist_ok=True)

        # Create the metadata file if it doesn't exist
        metadata_file_path = os.path.join(server_dir, METADATA_FILE_NAME)
        if not os.path.exists(metadata_file_path):
            generate_metadata_file(schema_name, schema_name, GENERIC_CLUB_NAME, GENERIC_CLUB_NAME)

        # Load the metadata file
        with open(metadata_file_path, 'r') as file:
            metadata = json.load(file)

        # Get the list of data objects in the schema
        data_objects = db.get_all_data_objects(engine, schema_name)

        # Iterate over the data objects
        for data in data_objects:
            # Get the new definition for the data object
            new_definition = get_new_definition(engine, data)
            if new_definition is not None:
                # Write the new definition to a file
                file_name = os.path.join(server_dir, f"{data['objectType']}_{data['objectName']}.sql")
                with open(file_name, 'w') as file:
                    file.write(new_definition)

    print("Metadata and object scripts generation completed.")


if __name__ == '__main__':
    main()
