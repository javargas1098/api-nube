import datetime
import os
import subprocess as sp
from celery import Celery
from celery.signals import task_postrun
from flask import current_app,Flask
from ..modelos import Task, TaskSchema,db
import requests

broker = os.environ['REDIS_URL']
backend = os.environ['REDIS_URL']
URL_ARCHIVOS = "http://ec2-3-224-135-28.compute-1.amazonaws.com"
celery  = Celery(__name__, broker=broker,
                backend=backend)

# celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", 'redis://default:mMpGhm5ioQWLoqgSVFLaKYf5X4gefrRd@redis-11258.c261.us-east-1-4.ec2.cloud.redislabs.com:11258')
# celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND",  'redis://default:mMpGhm5ioQWLoqgSVFLaKYf5X4gefrRd@redis-11258.c261.us-east-1-4.ec2.cloud.redislabs.com:11258')

celery.conf.broker_pool_limit = 0

def create_app(config_name):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://ruxgatsybvdqdm:15646d69ee12108cbf4e31f2bcc4e07114d4252d2a007a661b01508b1f34b228@ec2-44-199-85-33.compute-1.amazonaws.com:5432/dec0l5i7soa43p"
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
        # file = open(output, "rb")
        file = requests.get(URL_ARCHIVOS+'/upload/'+filename) 
        sendFile = {"file": file}
        content = requests.post(urlFile+'/files',files=sendFile, data=values,verify=False)
        print(content)
        print("2******")
        os.remove(output)              
    return True

