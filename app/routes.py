from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from app.models import User
from app import db
from werkzeug.security import check_password_hash

# Buat blueprint untuk route utama
main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role

            flash('Login berhasil!', 'success')
            return redirect(url_for('main.dashboard'))
        
        flash('Email atau password salah', 'danger')
        return redirect(url_for('main.login'))

    return render_template('login.html')


@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        
        new_user = User(username=username, email=email, role=role)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('main.login'))
    
    return render_template('register.html')

@main.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Anda harus login terlebih dahulu.', 'danger')
        return redirect(url_for('main.login'))
    
    users = User.query.all()
    
    current_user_role = session.get('role', None)
    
    return render_template('dashboard.html', users=users, current_user_role=current_user_role)


@main.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Anda tidak memiliki izin untuk mengakses halaman ini.', 'danger')
        return redirect(url_for('main.dashboard'))  # Redirect jika bukan admin
    
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        user.role = request.form['role']
        
        db.session.commit()
        flash('User berhasil diupdate!', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('edit_user.html', user=user)

@main.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Anda tidak memiliki izin untuk mengakses halaman ini.', 'danger')
        return redirect(url_for('main.dashboard'))  # Redirect jika bukan admin
    
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User berhasil dihapus!', 'success')
    return redirect(url_for('main.dashboard'))

@main.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Anda tidak memiliki izin untuk mengakses halaman ini.', 'danger')
        return redirect(url_for('main.dashboard'))  # Redirect jika bukan admin
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        
        # Cek apakah email sudah terdaftar
        if User.query.filter_by(email=email).first():
            flash('Email sudah terdaftar!', 'danger')
            return redirect(url_for('main.add_user'))
        
        # Buat user baru
        new_user = User(username=username, email=email, role=role)
        new_user.set_password(password)  # Hash password
        db.session.add(new_user)
        db.session.commit()
        
        flash('User baru berhasil ditambahkan!', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('add_user.html')


@main.route('/logout')
def logout():
    session.clear()
    flash('Anda telah logout.', 'success')
    return redirect(url_for('main.home'))
