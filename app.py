from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import pandas as pd
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hospital-management-secret-key'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'hospital.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(100))
    address = db.Column(db.Text)
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    pin_code = db.Column(db.String(10))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(100))

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(20), default='scheduled')
    patient = db.relationship('Patient', backref='appointments')
    doctor = db.relationship('Doctor', backref='appointments')

class Medicine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    stock = db.Column(db.Integer, default=0)
    price = db.Column(db.Float, nullable=False)
    expiry_date = db.Column(db.Date)

class Bill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    patient = db.relationship('Patient', backref='bills')

# Routes
@app.route('/')
def index():
    patients_count = Patient.query.count()
    doctors_count = Doctor.query.count()
    appointments_count = Appointment.query.count()
    medicines_count = Medicine.query.count()
    return render_template('dashboard.html', 
                         patients_count=patients_count,
                         doctors_count=doctors_count,
                         appointments_count=appointments_count,
                         medicines_count=medicines_count)

@app.route('/patients')
def patients():
    search = request.args.get('search', '').strip()
    gender_filter = request.args.get('gender', '').strip()
    
    # Get patients who don't have any paid bills
    paid_patient_ids = db.session.query(Bill.patient_id).filter(Bill.status == 'paid').distinct().all()
    paid_patient_ids = [pid[0] for pid in paid_patient_ids]
    
    query = Patient.query.filter(~Patient.id.in_(paid_patient_ids))
    
    # Apply search filter
    if search:
        query = query.filter(
            (Patient.name.contains(search)) |
            (Patient.phone.contains(search))
        )
    
    # Apply gender filter
    if gender_filter and gender_filter != '':
        query = query.filter(Patient.gender == gender_filter)
    
    patients = query.all()
    return render_template('patients.html', patients=patients, search=search, gender_filter=gender_filter)



@app.route('/add_patient', methods=['GET', 'POST'])
def add_patient():
    if request.method == 'POST':
        patient = Patient(
            name=request.form['name'],
            phone=request.form['phone'],
            email=request.form['email'],
            address=request.form['address'],
            city=request.form['city'],
            state=request.form['state'],
            pin_code=request.form['pin_code'],
            age=int(request.form['age']),
            gender=request.form['gender']
        )
        db.session.add(patient)
        db.session.commit()
        flash('Patient added successfully')
        return redirect(url_for('patients'))
    return render_template('add_patient.html')

@app.route('/view_patient/<int:id>')
def view_patient(id):
    patient = Patient.query.get_or_404(id)
    return render_template('view_patient.html', patient=patient)

@app.route('/edit_patient/<int:id>', methods=['GET', 'POST'])
def edit_patient(id):
    patient = Patient.query.get_or_404(id)
    if request.method == 'POST':
        patient.name = request.form['name']
        patient.phone = request.form['phone']
        patient.email = request.form['email']
        patient.address = request.form['address']
        patient.city = request.form['city']
        patient.state = request.form['state']
        patient.pin_code = request.form['pin_code']
        patient.age = int(request.form['age'])
        patient.gender = request.form['gender']
        db.session.commit()
        flash('Patient updated successfully')
        return redirect(url_for('patients'))
    return render_template('edit_patient.html', patient=patient)

@app.route('/delete_patient/<int:id>')
def delete_patient(id):
    patient = Patient.query.get_or_404(id)
    
    # Delete related appointments
    Appointment.query.filter_by(patient_id=id).delete()
    
    # Delete related bills
    Bill.query.filter_by(patient_id=id).delete()
    
    # Delete the patient
    db.session.delete(patient)
    db.session.commit()
    flash('Patient and all related records deleted successfully')
    return redirect(url_for('patients'))

@app.route('/doctors')
def doctors():
    doctors = Doctor.query.all()
    return render_template('doctors.html', doctors=doctors)

@app.route('/add_doctor', methods=['GET', 'POST'])
def add_doctor():
    if request.method == 'POST':
        doctor = Doctor(
            name=request.form['name'],
            specialization=request.form['specialization'],
            phone=request.form['phone'],
            email=request.form['email']
        )
        db.session.add(doctor)
        db.session.commit()
        flash('Doctor added successfully')
        return redirect(url_for('doctors'))
    return render_template('add_doctor.html')

@app.route('/edit_doctor/<int:id>', methods=['GET', 'POST'])
def edit_doctor(id):
    doctor = Doctor.query.get_or_404(id)
    if request.method == 'POST':
        doctor.name = request.form['name']
        doctor.specialization = request.form['specialization']
        doctor.phone = request.form['phone']
        doctor.email = request.form['email']
        db.session.commit()
        flash('Doctor updated successfully')
        return redirect(url_for('doctors'))
    return render_template('edit_doctor.html', doctor=doctor)

@app.route('/delete_doctor/<int:id>')
def delete_doctor(id):
    doctor = Doctor.query.get_or_404(id)
    db.session.delete(doctor)
    db.session.commit()
    flash('Doctor deleted successfully')
    return redirect(url_for('doctors'))

@app.route('/appointments')
def appointments():
    appointments = Appointment.query.all()
    return render_template('appointments.html', appointments=appointments)

@app.route('/add_appointment', methods=['GET', 'POST'])
def add_appointment():
    if request.method == 'POST':
        appointment = Appointment(
            patient_id=int(request.form['patient_id']),
            doctor_id=int(request.form['doctor_id']),
            date=datetime.strptime(request.form['date'], '%Y-%m-%d').date(),
            time=request.form['time']
        )
        db.session.add(appointment)
        db.session.commit()
        flash('Appointment scheduled successfully')
        return redirect(url_for('appointments'))
    patients = Patient.query.all()
    doctors = Doctor.query.all()
    return render_template('add_appointment.html', patients=patients, doctors=doctors)

@app.route('/edit_appointment/<int:id>', methods=['GET', 'POST'])
def edit_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    if request.method == 'POST':
        appointment.patient_id = int(request.form['patient_id'])
        appointment.doctor_id = int(request.form['doctor_id'])
        appointment.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        appointment.time = request.form['time']
        appointment.status = request.form['status']
        db.session.commit()
        flash('Appointment updated successfully')
        return redirect(url_for('appointments'))
    patients = Patient.query.all()
    doctors = Doctor.query.all()
    return render_template('edit_appointment.html', appointment=appointment, patients=patients, doctors=doctors)

@app.route('/delete_appointment/<int:id>')
def delete_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    db.session.delete(appointment)
    db.session.commit()
    flash('Appointment deleted successfully')
    return redirect(url_for('appointments'))

@app.route('/pharmacy')
def pharmacy():
    medicines = Medicine.query.all()
    return render_template('pharmacy.html', medicines=medicines)

@app.route('/add_medicine', methods=['GET', 'POST'])
def add_medicine():
    if request.method == 'POST':
        medicine_name = request.form['name'].strip()
        
        # Check if medicine already exists
        existing_medicine = Medicine.query.filter_by(name=medicine_name).first()
        if existing_medicine:
            flash('Medicine already exists! Please update the existing one or use a different name.')
            return redirect(url_for('add_medicine'))
        
        medicine = Medicine(
            name=medicine_name,
            stock=int(request.form['stock']),
            price=float(request.form['price']),
            expiry_date=datetime.strptime(request.form['expiry_date'], '%Y-%m-%d').date()
        )
        db.session.add(medicine)
        db.session.commit()
        flash('Medicine added successfully')
        return redirect(url_for('pharmacy'))
    return render_template('add_medicine.html')

@app.route('/edit_medicine/<int:id>', methods=['GET', 'POST'])
def edit_medicine(id):
    medicine = Medicine.query.get_or_404(id)
    if request.method == 'POST':
        medicine.name = request.form['name']
        medicine.stock = int(request.form['stock'])
        medicine.price = float(request.form['price'])
        medicine.expiry_date = datetime.strptime(request.form['expiry_date'], '%Y-%m-%d').date()
        db.session.commit()
        flash('Medicine updated successfully')
        return redirect(url_for('pharmacy'))
    return render_template('edit_medicine.html', medicine=medicine)

@app.route('/delete_medicine/<int:id>')
def delete_medicine(id):
    medicine = Medicine.query.get_or_404(id)
    db.session.delete(medicine)
    db.session.commit()
    flash('Medicine deleted successfully')
    return redirect(url_for('pharmacy'))

@app.route('/search_medicines')
def search_medicines():
    query = request.args.get('q', '').lower()
    try:
        # Read CSV file
        csv_path = os.path.join(os.path.dirname(__file__), 'A_Z_medicines_dataset_of_India.csv')
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            
            # Filter medicines based on query
            if 'Medicine Name' in df.columns:
                medicines = df['Medicine Name'].dropna().unique()
            elif 'name' in df.columns:
                medicines = df['name'].dropna().unique()
            else:
                medicines = df.iloc[:, 0].dropna().unique()  # Use first column
            
            # Filter medicines that start with the query
            filtered = [med for med in medicines if str(med).lower().startswith(query)][:15]
            return jsonify(filtered)
        else:
            # Fallback medicine list if CSV not found
            medicines = ['Paracetamol', 'Aspirin', 'Ibuprofen', 'Amoxicillin', 'Ciprofloxacin']
            filtered = [med for med in medicines if med.lower().startswith(query)][:15]
            return jsonify(filtered)
    except:
        return jsonify([])

@app.route('/search_cities')
def search_cities():
    query = request.args.get('q', '').strip().lower()
    
    if not query:
        return jsonify([])
    
    try:
        csv_path = os.path.join(os.path.dirname(__file__), 'india_cities_list.csv')
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            cities = df['City'].dropna().tolist()
            filtered = [city for city in cities if city.lower().startswith(query)][:15]
            return jsonify(filtered)
        else:
            # Fallback city list if CSV not found
            cities = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad', 'Pune', 'Ahmedabad']
            filtered = [city for city in cities if city.lower().startswith(query)][:15]
            return jsonify(filtered)
    except:
        return jsonify([])

@app.route('/search_states')
def search_states():
    query = request.args.get('q', '').strip().lower()
    
    if not query:
        return jsonify([])
    
    try:
        csv_path = os.path.join(os.path.dirname(__file__), 'india_states_list.csv')
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            states = df['State'].dropna().tolist()
            filtered = [state for state in states if state.lower().startswith(query)][:15]
            return jsonify(filtered)
        else:
            # Fallback state list if CSV not found
            states = ['Maharashtra', 'Delhi', 'Karnataka', 'Tamil Nadu', 'West Bengal', 'Telangana', 'Gujarat', 'Rajasthan']
            filtered = [state for state in states if state.lower().startswith(query)][:15]
            return jsonify(filtered)
    except:
        return jsonify([])

@app.route('/billing')
def billing():
    bills = Bill.query.filter_by(status='pending').all()
    return render_template('billing.html', bills=bills)

@app.route('/add_bill', methods=['GET', 'POST'])
def add_bill():
    if request.method == 'POST':
        bill = Bill(
            patient_id=int(request.form['patient_id']),
            amount=float(request.form['amount']),
            description=request.form['description']
        )
        db.session.add(bill)
        db.session.commit()
        flash('Bill created successfully')
        return redirect(url_for('billing'))
    patients = Patient.query.all()
    return render_template('add_bill.html', patients=patients)

@app.route('/view_bill/<int:id>')
def view_bill(id):
    bill = Bill.query.get_or_404(id)
    return render_template('view_bill.html', bill=bill)

@app.route('/edit_bill/<int:id>', methods=['GET', 'POST'])
def edit_bill(id):
    bill = Bill.query.get_or_404(id)
    if request.method == 'POST':
        bill.patient_id = int(request.form['patient_id'])
        bill.amount = float(request.form['amount'])
        bill.description = request.form['description']
        db.session.commit()
        flash('Bill updated successfully')
        return redirect(url_for('billing'))
    patients = Patient.query.all()
    return render_template('edit_bill.html', bill=bill, patients=patients)

@app.route('/delete_bill/<int:id>')
def delete_bill(id):
    bill = Bill.query.get_or_404(id)
    db.session.delete(bill)
    db.session.commit()
    flash('Bill deleted successfully')
    return redirect(url_for('billing'))

@app.route('/history')
def history():
    paid_bills = Bill.query.filter_by(status='paid').all()
    return render_template('history.html', paid_bills=paid_bills)

@app.route('/mark_paid/<int:id>')
def mark_paid(id):
    bill = Bill.query.get_or_404(id)
    
    # Check if patient has completed appointment
    completed_appointment = Appointment.query.filter_by(
        patient_id=bill.patient_id, 
        status='completed'
    ).first()
    
    if not completed_appointment:
        flash('Cannot mark bill as paid. Patient appointment is not completed yet.')
        return redirect(url_for('billing'))
    
    bill.status = 'paid'
    db.session.commit()
    flash('Bill marked as paid and moved to history')
    return redirect(url_for('billing'))

@app.route('/restore_bill/<int:id>')
def restore_bill(id):
    bill = Bill.query.get_or_404(id)
    bill.status = 'pending'
    db.session.commit()
    flash('Bill restored to active billing')
    return redirect(url_for('history'))

def init_db():
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    init_db()
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)