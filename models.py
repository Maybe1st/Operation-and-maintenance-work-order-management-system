from datetime import datetime
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

ROLE_USER = '普通用户'
ROLE_ADMIN = 'admin'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default=ROLE_USER)

    tickets_handled = db.relationship('Ticket', backref='handler_obj', lazy='dynamic', foreign_keys='Ticket.handler_id')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == ROLE_ADMIN or self.role == '管理员'

    def __repr__(self):
        return f'<User {self.username}>'


class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='待处理')

    handler_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    handler = db.relationship('User', foreign_keys=[handler_id], uselist=False)

    location = db.Column(db.String(100), nullable=True)
    reporter = db.Column(db.String(100), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 方案中的乐观锁字段
    version = db.Column(db.Integer, nullable=False, default=1)

    # AI 可观测性字段
    classification_source = db.Column(db.String(32), nullable=True)
    classification_confidence = db.Column(db.Float, nullable=True)
    classification_model = db.Column(db.String(128), nullable=True)
    classification_latency_ms = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f'<Ticket {self.id} - {self.ticket_type}>'


class TicketOperationLog(db.Model):
    __tablename__ = 'ticket_operation_logs'
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=False)
    operator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    action = db.Column(db.String(64), nullable=False)
    from_status = db.Column(db.String(50))
    to_status = db.Column(db.String(50))
    remark = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    operator = db.relationship('User', foreign_keys=[operator_id])
    ticket = db.relationship('Ticket', foreign_keys=[ticket_id])
