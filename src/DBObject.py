import os

ROOT_FOLDER_NAME = 'Club_handler'
BASE_DIR = str(os.getcwd())[:os.getcwd().index(ROOT_FOLDER_NAME) + len(ROOT_FOLDER_NAME)]


class DBObject:
    def __init__(self, relative_path, project_name, schema_name, object_name, object_type):
        self.relative_path = os.path.join(BASE_DIR, relative_path)
        self.project_name = project_name
        self.schema_name = schema_name
        self.object_name = object_name
        self.object_type = object_type
        self.dependencies = []
        self.definition = ''
        objects_path = os.path.join(self.relative_path, self.project_name, self.schema_name, '01-tables')
        if not os.path.exists(objects_path):
            os.makedirs(objects_path)

    def __str__(self):
        return '{} Name: {}\nDependencies: {}'.format(self.object_type, self.object_name, ', '.join(self.dependencies))

    def commit(self):
        return self._commit_file(self.object_name)

    def _commit_file(self, file_name):
        try:
            full_path = os.path.join(self.relative_path, self.project_name, self.schema_name, '01-tables')
            with open(os.path.join(full_path, file_name + '.sql'), 'w') as file:
                file.write(self.definition)
            with open(os.path.join(full_path, file_name + '.txt'), 'w') as file:
                file.write(','.join(self.dependencies))
            return True, 'File Added.'
        except Exception as e:
            return False, 'Commit Failed: {}'.format(e)

    def set_definition(self, definition):
        self.definition = definition

    def set_dependencies(self, dependencies):
        self.dependencies = dependencies


class Table(DBObject):
    def __init__(self, relative_path, project_name, schema_name, table_name):
        super().__init__(relative_path, project_name, schema_name, table_name, 'Table')


class View(DBObject):
    def __init__(self, relative_path, project_name, schema_name, view_name):
        super().__init__(relative_path, project_name, schema_name, view_name, 'View')


class StoredProcedure(DBObject):
    def __init__(self, relative_path, project_name, schema_name, procedure_name):
        super().__init__(relative_path, project_name, schema_name, procedure_name, 'Procedure')
