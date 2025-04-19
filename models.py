from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'doctor' or 'admin'

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"

class Box(db.Model):
    __tablename__ = 'boxes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=False)  # e.g. 'available', 'occupied', 'maintenance'
    equipment = db.relationship('Equipment', backref='box', lazy=True)
    availability = db.relationship('Availability', backref='box', lazy=True)

    def __repr__(self):
        return f"<Box {self.name} ({self.status})>"

class Equipment(db.Model):
    __tablename__ = 'equipment'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    box_id = db.Column(db.Integer, db.ForeignKey('boxes.id'), nullable=False)

    def __repr__(self):
        return f"<Equipment {self.name} in Box {self.box_id}>"

class Availability(db.Model):
    __tablename__ = 'availability'
    id = db.Column(db.Integer, primary_key=True)
    box_id = db.Column(db.Integer, db.ForeignKey('boxes.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    is_available = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"<Availability Box {self.box_id} on {self.date} Available: {self.is_available}>"

class Appointment(db.Model):
    __tablename__ = 'appointments'
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    box_id = db.Column(db.Integer, db.ForeignKey('boxes.id'), nullable=False)
    appointment_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='scheduled')  # e.g. scheduled, completed, cancelled

    doctor = db.relationship('User', backref='appointments')
    box = db.relationship('Box', backref='appointments')

    def __repr__(self):
        return f"<Appointment Doctor {self.doctor_id} Box {self.box_id} at {self.appointment_time}>"
