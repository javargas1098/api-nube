from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restful import Api

# from flaskr import create_app

from .modelos import db
from .vistas import VistaSignIn, VistaLogIn, VistaTasks, VistaTaskDetail, VistaFileDetail,VistaTest
UPLOAD_FOLDER = 'uploaded'
DOWNLOAD_FOLDER = 'download'
UPLOAD_FOLDER_FACES = '/tmp/'

def create_app(config_name):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:uniandes@db-0001.cexmvypaid2k.us-east-1.rds.amazonaws.com:5432/postgres"
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
    app.config['UPLOAD_FOLDER_FACES']=UPLOAD_FOLDER_FACES
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'frase-secreta'
    app.config['PROPAGATE_EXCEPTIONS'] = True
    return app

app = create_app('default')
app_context = app.app_context()
app_context.push()

db.init_app(app)
db.create_all()
cors = CORS(app)

api = Api(app)

api.add_resource(VistaSignIn, '/api/auth/signup')
api.add_resource(VistaLogIn, '/api/auth/login')
api.add_resource(VistaTasks, '/api/tasks')
api.add_resource(VistaTaskDetail, '/api/tasks/<int:task_id>')
api.add_resource(VistaFileDetail, '/api/files/<string:file_name>')
api.add_resource(VistaTest, '/')
jwt = JWTManager(app)

