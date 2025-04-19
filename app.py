from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Box, Equipment, Appointment, Availability
from config import Config
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_request
def create_tables():
    db.create_all()

@app.route('/')
def inicio():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif current_user.role == 'doctor':
            return redirect(url_for('doctor_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nombre_usuario = request.form.get('username')
        contrasena = request.form.get('password')
        usuario = User.query.filter_by(username=nombre_usuario).first()
        if usuario and check_password_hash(usuario.password, contrasena):
            login_user(usuario)
            flash('Inicio de sesión exitoso.', 'success')
            siguiente_pagina = request.args.get('next')
            return redirect(siguiente_pagina or url_for('inicio'))
        else:
            flash('Nombre de usuario o contraseña inválidos.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión.', 'info')
    return redirect(url_for('login'))

from flask import jsonify

@app.route('/admin/dashboard')
@login_required
def panel_administrador():
    if current_user.role != 'admin':
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('inicio'))
    boxes = Box.query.all()
    medicos = User.query.filter_by(role='doctor').all()
    turnos = Appointment.query.order_by(Appointment.appointment_time).all()
    return render_template('admin_dashboard.html', boxes=boxes, medicos=medicos, turnos=turnos)

@app.route('/admin/disponibilidad', methods=['GET', 'POST'])
@login_required
def gestionar_disponibilidad():
    if current_user.role != 'admin':
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('inicio'))
    if request.method == 'POST':
        id_box = request.form.get('box_id')
        fecha_str = request.form.get('date')
        disponible = request.form.get('is_available') == 'on'
        fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        disponibilidad = Availability.query.filter_by(box_id=id_box, date=fecha_obj).first()
        if disponibilidad:
            disponibilidad.is_available = disponible
        else:
            disponibilidad = Availability(box_id=id_box, date=fecha_obj, is_available=disponible)
            db.session.add(disponibilidad)
        db.session.commit()
        flash('Disponibilidad actualizada.', 'success')
        return redirect(url_for('gestionar_disponibilidad'))
    boxes = Box.query.all()
    disponibilidades = Availability.query.order_by(Availability.date.desc()).all()
    return render_template('manage_availability.html', boxes=boxes, availabilities=disponibilidades)

@app.route('/admin/asignar_turno', methods=['GET', 'POST'])
@login_required
def asignar_turno():
    if current_user.role != 'admin':
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('inicio'))
    if request.method == 'POST':
        id_medico = request.form.get('doctor_id')
        id_box = request.form.get('box_id')
        fecha_hora_str = request.form.get('appointment_time')
        fecha_hora = datetime.strptime(fecha_hora_str, '%Y-%m-%dT%H:%M')
        turno = Appointment(doctor_id=id_medico, box_id=id_box, appointment_time=fecha_hora, status='scheduled')
        db.session.add(turno)
        db.session.commit()
        flash('Turno asignado correctamente.', 'success')
        return redirect(url_for('panel_administrador'))
    medicos = User.query.filter_by(role='doctor').all()
    boxes = Box.query.all()
    return render_template('assign_appointment.html', doctors=medicos, boxes=boxes)

@app.route('/doctor/dashboard')
@login_required
def panel_medico():
    if current_user.role != 'doctor':
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('inicio'))
    turnos = Appointment.query.filter_by(doctor_id=current_user.id).order_by(Appointment.appointment_time).all()
    return render_template('doctor_dashboard.html', appointments=turnos)

if __name__ == '__main__':
    app.run(debug=True, port=8000)
