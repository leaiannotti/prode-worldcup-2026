from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from authlib.integrations.flask_client import OAuth

# Initialize extensions without binding to app
db = SQLAlchemy()
migrate = Migrate()
oauth = OAuth()
