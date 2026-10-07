import os
from flask import Flask, flash, redirect, url_for
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from functools import wraps

from extensions import db, login_manager
from models import User


def _build_admin_required():
    def admin_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or (current_user.role != 'admin' and current_user.role != '管理员'):
                flash('您没有权限访问此页面。', 'danger')
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    return admin_required


def create_app(config_object=None):
    app = Flask(__name__)
    app.jinja_env.add_extension('jinja2.ext.do')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_very_secret_key_that_you_should_change')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///site.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    if config_object:
        app.config.from_object(config_object)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message_category = 'info'
    Migrate(app, db)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.admin_required = _build_admin_required()

    auto_init_db = os.environ.get('AUTO_INIT_DB', '1') == '1'
    if auto_init_db:
        with app.app_context():
            db.create_all()
            if not User.query.filter_by(username='admin').first():
                admin_user = User(username='admin', role='admin')
                admin_user.set_password(os.environ.get('DEFAULT_ADMIN_PASSWORD', 'admin123'))
                db.session.add(admin_user)
                db.session.commit()
                print('已创建默认管理员用户：admin/admin123')

    from routes import *
    try:
        from api.routes import api_bp
        app.register_blueprint(api_bp, url_prefix='/api/v1')
    except Exception:
        pass

    return app


app = create_app()


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=os.environ.get('FLASK_DEBUG', '0') == '1')
