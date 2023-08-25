from config import MYSQL_CONFIG
from flask import send_file
import MySQLdb
import pathlib
import zipfile
import io
from collections import defaultdict
import shutil


class Cursor:
    def __init__(self):
        self.connection = MySQLdb.connect(**MYSQL_CONFIG, autocommit=True)
        self.cursor = self.connection.cursor()
    
    def __enter__(self):
        return self.cursor
    
    def __exit__(self, *args):
        self.cursor.close()
        self.connection.close()


class File:
    def __init__(self, file):
        self.file = file
        self.path = pathlib.Path(self.file.filename)
        self.filename = self.path.name

        extension_separator = self.filename.find('.')

        self.stem = self.filename[0:extension_separator]

        frame_separator = self.stem.rfind('-')

        self.name = self.stem[0:frame_separator]
        self.frame = self.stem[frame_separator+1:]

        self.valid = is_available(self.name) and self.frame in ['before', 'after']
    
    def save(self, experiment_id):
        save_path = get_experiment_directory_path(experiment_id) / self.filename

        if not save_path.parent.exists():
            save_path.parent.mkdir()

        self.file.save(save_path)


def get_experiment_directory_path(experiment_id):
    return pathlib.Path(f'/home/elifast/work/CellTracker/experiments/{experiment_id}')


def get(exclude_completed=False, exclude_errors=False):
    with Cursor() as cursor:
        if exclude_completed and exclude_errors:
            query = 'SELECT * FROM experiments WHERE status < 3 AND status != -1'
        elif exclude_completed:
            query = 'SELECT * FROM experiments WHERE status < 3'
        elif exclude_errors:
            query = 'SELECT * FROM experiments WHERE status != -1'
        else:
            query = 'SELECT * FROM experiments'

        cursor.execute(query)
        
        return cursor.fetchall()


def get_experiments_info(experiment_ids):
    with Cursor() as cursor:
        query = f'SELECT * FROM experiments WHERE id in ({str(experiment_ids)[1:-1]})'  # very clever

        cursor.execute(query)

        return cursor.fetchall()
    

def delete(experiment_ids):
    with Cursor() as cursor:
        query = f'DELETE FROM experiments WHERE id in ({str(experiment_ids)[1:-1]})'

        cursor.execute(query)
    
    for experiment_id in experiment_ids:
        experiment_directory_path = get_experiment_directory_path(experiment_id)

        shutil.rmtree(experiment_directory_path)


def is_available(experiment_name):
    with Cursor() as cursor:
        query = f'SELECT id FROM experiments WHERE name = \'{experiment_name}\''

        cursor.execute(query)

        return cursor.fetchone() is None


def create_experiment(files):   
    with Cursor() as cursor:
        cursor.execute(f'INSERT INTO experiments (name) VALUES (\'{files[0].name}\')')
        cursor.execute('SELECT LAST_INSERT_ID()')

        experiment_id = cursor.fetchone()[0]
    
    files[0].save(experiment_id)
    files[1].save(experiment_id)


def process_files(files):
    files = [File(file) for file in files]
    file_dictionary = defaultdict(list)

    for file in files:
        if file.valid:
            file_dictionary[file.name].append(file)
    
    for key in file_dictionary:
        files = file_dictionary[key]

        if len(files) == 2 and (files[0].frame == 'before' or files[1].frame == 'before'):
            create_experiment(files)


def increment_status(experiment_id):
    with Cursor() as cursor:
        query = f'UPDATE experiments SET status = status + 1 WHERE id = {experiment_id}'

        cursor.execute(query)


def set_status(experiment_id, status):
    with Cursor() as cursor:
        query = f'UPDATE experiments SET status = {status} WHERE id = {experiment_id}'

        cursor.execute(query)


def send_zipfile(experiment_ids):
    data = io.BytesIO()

    experiments_info = get_experiments_info(experiment_ids)

    with zipfile.ZipFile(data, 'w') as zip_file:
        for experiment_id, name, _ in experiments_info:
            experiment_directory_path = get_experiment_directory_path(experiment_id)
            results_file_path = experiment_directory_path / 'results.csv'
            visualization_file_path = experiment_directory_path / 'visualization.png'

            if not results_file_path.exists():
                continue

            zip_results_path = pathlib.Path(f'data/{name}.csv')
            zip_visualization_path = pathlib.Path(f'data/{name}.png')
            
            zip_file.write(results_file_path, arcname=zip_results_path)
            zip_file.write(visualization_file_path, arcname=zip_visualization_path)
    
    data.seek(0)
    
    return send_file(
        data,
        mimetype='application/zip',
        as_attachment=True,
        download_name=f'data.zip'
    )


# set_status(3, 0)
