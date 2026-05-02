from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.secret_key = 'lifestream_secret_key'

# Database Configuration
# Successfully connected to PostgreSQL with password '1234'
PG_PASS = '1234'
PG_URL = f'postgresql://postgres:{PG_PASS}@localhost:5432/lifestream'

def init_db():
    try:
        import psycopg2
        from psycopg2 import sql
        # Connect to default 'postgres' to create 'lifestream' if missing
        conn = psycopg2.connect(dbname="postgres", user="postgres", password=PG_PASS, host="localhost")
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM pg_database WHERE datname = 'lifestream'")
        if not cur.fetchone():
            cur.execute(sql.SQL("CREATE DATABASE lifestream"))
            print("Database 'lifestream' created.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error initializing PostgreSQL: {e}")

init_db()
app.config['SQLALCHEMY_DATABASE_URI'] = PG_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class Donor(db.Model):
    __tablename__ = 'donors'
    donor_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    blood_group = db.Column(db.String(5), nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    last_donation_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class BloodStock(db.Model):
    __tablename__ = 'blood_stock'
    stock_id = db.Column(db.Integer, primary_key=True)
    blood_group = db.Column(db.String(5), unique=True, nullable=False)
    quantity_ml = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class BloodRequest(db.Model):
    __tablename__ = 'requests'
    request_id = db.Column(db.Integer, primary_key=True)
    hospital_name = db.Column(db.String(150), nullable=False)
    blood_group_required = db.Column(db.String(5), nullable=False)
    quantity_required_ml = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='Pending')
    request_date = db.Column(db.DateTime, default=datetime.utcnow)

# Routes
@app.route('/')
def dashboard():
    stocks = BloodStock.query.order_by(BloodStock.blood_group).all()
    all_donors = Donor.query.order_by(Donor.created_at.desc()).all()
    all_requests = BloodRequest.query.order_by(BloodRequest.request_date.desc()).all()
    return render_template('dashboard.html', stocks=stocks, donors=all_donors, requests=all_requests)

@app.route('/add_donor', methods=['GET', 'POST'])
def add_donor():
    if request.method == 'POST':
        name = request.form['name']
        blood_group = request.form['blood_group']
        phone = request.form['phone']
        
        # Check if donor already exists
        existing_donor = Donor.query.filter_by(phone=phone).first()
        if existing_donor:
            # Check eligibility (3 months = 90 days)
            if existing_donor.last_donation_date:
                gap = datetime.now().date() - existing_donor.last_donation_date
                if gap.days < 90:
                    flash(f"Donor not eligible yet. Last donation was {gap.days} days ago.", "danger")
                    return redirect(url_for('add_donor'))
            
            # Update donor record
            existing_donor.last_donation_date = datetime.now().date()
            flash("Existing donor record updated.", "success")
        else:
            # Create new donor
            new_donor = Donor(name=name, blood_group=blood_group, phone=phone, last_donation_date=datetime.now().date())
            db.session.add(new_donor)
            flash("New donor added successfully.", "success")
        
        # Update stock
        stock = BloodStock.query.filter_by(blood_group=blood_group).first()
        if stock:
            stock.quantity_ml += 450  # Average donation is 450ml
        else:
            new_stock = BloodStock(blood_group=blood_group, quantity_ml=450)
            db.session.add(new_stock)
        
        db.session.commit()
        return redirect(url_for('dashboard'))
    
    return render_template('add_donor.html')

@app.route('/request_blood', methods=['GET', 'POST'])
def request_blood():
    if request.method == 'POST':
        hospital = request.form['hospital']
        blood_group = request.form['blood_group']
        qty = int(request.form['quantity'])
        
        new_request = BloodRequest(hospital_name=hospital, blood_group_required=blood_group, quantity_required_ml=qty)
        db.session.add(new_request)
        db.session.commit()
        flash("Blood request submitted.", "info")
        return redirect(url_for('dashboard'))
    
    return render_template('request_blood.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Initialize stock if empty
        if not BloodStock.query.first():
            groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
            for g in groups:
                db.session.add(BloodStock(blood_group=g, quantity_ml=0))
            db.session.commit()
            
    app.run(debug=True, host='0.0.0.0', port=5000)
