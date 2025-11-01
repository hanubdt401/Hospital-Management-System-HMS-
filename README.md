# 🏥 Hospital Management System


A comprehensive web-based Hospital Management System built with Flask and SQLite.

## Features

- **👨⚕️ Patient Management**: Register, view, and manage patient records
- **🩺 Doctor Management**: Add doctors with specializations and contact info
- **📅 Appointment Scheduling**: Book and manage patient-doctor appointments
- **💊 Pharmacy Management**: Track medicine inventory and stock levels
- **🧾 Billing System**: Generate and manage patient bills
- **🔐 User Authentication**: Secure login system with role-based access

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**
   ```bash
   python app.py
   ```

3. **Access the System**
   - Open browser: http://localhost:5000
   - Login: admin / admin123

## Project Structure

```
Hospital Management System/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── templates/          # HTML templates
│   ├── base.html      # Base template with navigation
│   ├── login.html     # Login page
│   ├── dashboard.html # Main dashboard
│   ├── patients.html  # Patient management
│   ├── doctors.html   # Doctor management
│   ├── appointments.html # Appointment scheduling
│   ├── pharmacy.html  # Medicine inventory
│   └── billing.html   # Billing system
└── hospital.db        # SQLite database (auto-created)
```

## Database Models

- **User**: Authentication and roles
- **Patient**: Patient information and medical records
- **Doctor**: Doctor profiles and specializations
- **Appointment**: Patient-doctor scheduling
- **Medicine**: Pharmacy inventory management
- **Bill**: Patient billing and payments

## Default Login

- Username: `admin`
- Password: `admin123`

## Technology Stack

- **Backend**: Python Flask
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML, Bootstrap 5, JavaScript
- **Authentication**: Werkzeug password hashing

