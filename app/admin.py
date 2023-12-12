from flask_admin.contrib.sqla import ModelView

from app import admin_app, db
from app.models import User, Cat, Role


class SecurityModelView(ModelView):
    column_display_pk = True


admin_app.add_view(SecurityModelView(User, db.session, endpoint='user'))
admin_app.add_view(SecurityModelView(Cat, db.session, endpoint='cat'))
admin_app.add_view(SecurityModelView(Role, db.session, endpoint='role'))
