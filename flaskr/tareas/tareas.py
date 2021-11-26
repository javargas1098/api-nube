import datetime
import os
import subprocess as sp
from celery import Celery
from celery.signals import task_postrun
from flask import current_app,Flask
from modelos import Task, TaskSchema,db
import requests

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", 'redis://redis:6379/0')
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND",  'redis://redis:6379/0')
celery.conf.broker_pool_limit = 0

def create_app(config_name):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://ipigpykpndprpi:89d9b3038afd98bacd2750e5c75de161df88c9f7a6cc19647b93875ee88304db@ec2-44-198-196-149.compute-1.amazonaws.com:5432/d5p22op6k4gur1"
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    app.config['JWT_SECRET_KEY']='frase-secreta'
    app.config['PROPAGATE_EXCEPTIONS'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    return app

@celery.task(name="file_save")
def file_save(request_json):
    app = create_app('default')
    db.init_app(app)
    with app.app_context():
        output = request_json["output"] 
        inputF  = request_json["inputF"]  
        urlFile = request_json["urlFile"] 
        filename = request_json["filename"]
        outputF = request_json["outputF"]
        creation_date = request_json["creation_date"]
        dfile = request_json["dfile"]
        identity = request_json["identity"]
        format = request_json["format"]
        ts = datetime.datetime.now()
        new_task = Task(name=filename, status="UPLOADED",
                        dateUp=ts, datePr=ts, nameFormat="", user=identity)
        db.session.add(new_task)
        db.session.commit()
        task_schema = TaskSchema()
        taskId = task_schema.dump(new_task)['id']
        values = {'fileType': format, 'taskId': task_schema.dump(new_task)['id']}
        file = open(output, "rb")
        sendFile = {"file": file}
        content = requests.post(urlFile+'/files',files=sendFile, data=values)
        print(content)
        print("2******")
        os.remove(output)              
    return True

