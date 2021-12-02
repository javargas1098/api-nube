import datetime
import io
import json
import time
import uuid
import os
import requests
from ..tareas import file_save
from flask import current_app,request, send_file
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from flask_restful import Resource
from ..modelos import db, User, Task, UserSchema, TaskSchema
from werkzeug.utils import secure_filename

user_schema = UserSchema()
task_schema = TaskSchema()

URL_CONVERSOR = "http://presentacion-conversor-1-613596235.us-east-1.elb.amazonaws.com"
URL_ARCHIVOS = "http://ec2-44-198-170-177.compute-1.amazonaws.com"


class VistaSignIn(Resource):

    def post(self):
        if request.json["password1"] != request.json["password2"]:
            return "Password do not match", 400
        else:
            new_user = User(
                username=request.json["username"], password=request.json["password1"], email=request.json["email"])
            db.session.add(new_user)
            db.session.commit()
            access_token = create_access_token(identity=new_user.id)
            return {"message": "User created successfully", "token": access_token}

    def delete(self, user_id):
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return '', 204


class VistaLogIn(Resource):

    def post(self):
        user = User.query.filter(
            User.username == request.json["username"], User.password == request.json["password"]).first()
        db.session.commit()
        if user is None:
            return "User not exit", 404
        else:
            token_de_acceso = create_access_token(identity=user.id)
            return {"message": "Successful login", "token": token_de_acceso}


class VistaTasks(Resource):

    @jwt_required()
    def get(self):
        identity = get_jwt_identity()
        query_string = "select * from task t where t.user =" + str(identity)
        result = db.engine.execute(query_string)
        return json.loads(json.dumps([dict(row) for row in result], default=myConverter))

    @jwt_required()
    def post(self):
        identity = get_jwt_identity()
        file = request.files['file']
        format = request.form.get("newFormat")
        filename = secure_filename(file.filename)
        filename = '{}.{}'.format(os.path.splitext(filename)[0] + str(uuid.uuid4()),
                                    os.path.splitext(filename)[1])  # Build input name    
        MYDIR = os.path.dirname(__file__).replace("vistas", "").replace("/app/","")                                                  
        output = os.path.join(current_app.config['UPLOAD_FOLDER_FACES'], filename)
        # file.save(output) 
        print(output)
       
        uuidSelected = uuid.uuid4()
        dfile = '{}.{}'.format(os.path.splitext(filename)[
                                    0] + str(uuidSelected), str(format))  # Build file name
        outputF = os.path.join(current_app.config['UPLOAD_FOLDER_FACES'], dfile)
        sendFile = {"file": (filename, file.stream, file.mimetype)}
        # sendFile = {"file": file}
        print(sendFile)
        cont=requests.post(URL_ARCHIVOS+'/upload',files=sendFile,verify=False)   
        inputF  = URL_CONVERSOR+'/files/'
        # json = {
        #     'output':output,
        #     'urlFile':URL_CONVERSOR,
        #     'outputF':outputF,
        #     'inputF':inputF,
        #     'filename':file.filename,
        #     'dfile':dfile,
        #     'format': request.form.get("newFormat"),
        #     'creation_date': str(int(time.time())),
        #     'identity':identity
        # }
        #args = (json,)
        # file_save.delay(json)
        ts = datetime.datetime.now()
        new_task = Task(name=filename, status="UPLOADED",
                        dateUp=ts, datePr=ts, nameFormat="", user=identity)
        db.session.add(new_task)
        db.session.commit()
        task_schema = TaskSchema()
        taskId = task_schema.dump(new_task)['id']
        values = {'fileType': format, 'taskId': task_schema.dump(new_task)['id']}
        content = requests.post(URL_CONVERSOR+'/files',files=sendFile, data=values,verify=False)
        print(content)  
        return "Task converted", 200  

 


class VistaTaskDetail(Resource):

    @jwt_required()
    def get(self, task_id):
        task = Task.query.get_or_404(task_id)
        return json.loads(json.dumps(task_schema.dump(task), default=myConverter))

    @jwt_required()
    def put(self, task_id):
        task = Task.query.get_or_404(task_id)
        taskJson = json.loads(json.dumps(task_schema.dump(task), default=myConverter))

        task.status = "UPLOADED"
        task.dateUp = datetime.datetime.now()
        db.session.commit()
        requests.put(URL_CONVERSOR +'/update-files',
                               json={'name': taskJson['name'], 'status': taskJson['status']['llave'], 'taskId': task_id,
                                     'nameFormat': taskJson['nameFormat'], 'newFormat': request.form.get('newFormat')},verify=False)
        return "Task updated", 200
       

    @jwt_required()
    def delete(self, task_id):
        task = Task.query.get_or_404(task_id)
        taskJson = json.loads(json.dumps(task_schema.dump(task), default=myConverter))

        requests.delete(URL_CONVERSOR+'/delete-files',
                                  json={'name': taskJson['name'], 'nameFormat': taskJson['nameFormat']},verify=False)
        db.session.delete(task)
        db.session.commit()
        return "Task deleted", 200
        


class VistaFileDetail(Resource):

    @jwt_required()
    def get(self, file_name):
        content = requests.get(URL_CONVERSOR+'/get-files/' + file_name, stream=True,verify=False)
        return send_file(io.BytesIO(content.content), as_attachment=True, attachment_filename=file_name)


def myConverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

class VistaTest(Resource):
    def get(self):
        return "funcionando"