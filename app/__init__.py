from flask import Flask
from flask_admin import Admin
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

from config import Config

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

db = SQLAlchemy(metadata=MetaData(naming_convention=convention))
migrate = Migrate()
admin_app = Admin(name='KursoAgregator', template_mode='bootstrap3')

app = Flask(__name__)
app.config.from_object(Config)
migrate.init_app(app, db,render_as_batch=True)
db.init_app(app)
admin_app.init_app(app)


from app import models, admin, routes, diffi_helman
