# 🏥 Hospital Management System

A professional, industry-level web application for managing hospital operations, built with Flask and SQLite.

**Created by Parth Kothawade**

## 🎯 Overview

This system provides a complete solution for hospital management with separate portals for patients, doctors, and administrators. It features real-time appointment booking, conflict prevention, medical records management, and comprehensive dashboards.

## ✨ Key Features

### For Patients 👤

- ✅ Self-registration and secure login
- 🔍 Search and filter doctors by specialization
- 📅 View doctor availability in real-time
- 🩺 Book appointments with conflict checking
- 📋 View appointment history and status
- ❌ Cancel appointments (24-hour policy)
- 💊 Access medical records (diagnosis, prescription)
- 📝 Manage personal and medical information

### For Doctors 👨‍⚕️

- ✅ Professional registration (requires admin verification)
- 📊 Comprehensive dashboard with statistics
- 🗓️ Flexible schedule management (time slots)
- 👥 View and manage patient appointments
- 📝 Add diagnosis, prescription, and notes
- ✓ Update appointment status (confirmed, completed, etc.)
- 📱 View patient medical history
- 👤 Professional profile management

### For Admins 🔐

- ✅ Verify doctor registrations
- 👁️ System oversight and monitoring
- 👥 Manage all users (patients, doctors)
- 📊 View system-wide statistics
- 🛠️ System configuration and maintenance

## 🏗️ Architecture

### Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript
- **Authentication**: Session-based with role management
- **Security**: SHA256 password hashing, SQL injection prevention

### Project Structure

```
Hospital_Management/
├── app.py                      # Main application (factory pattern)
├── config.py                   # Environment-based configuration
├── models.py                   # Database models (User, Doctor, Patient, etc.)
├── utils.py                    # Utilities (auth decorators, password hashing)
├── run.py                      # Application runner
├── requirements.txt            # Python dependencies
├── database_schema.sql         # Complete database schema
├── email_service.py            # Email notification service
├── send_reminders.py           # Automated appointment reminders
│
├── routes/                     # Blueprint modules
│   ├── main.py                # Home and general routes
│   ├── auth.py                # Authentication (login, register, logout)
│   ├── doctor.py              # Doctor portal routes
│   ├── patient.py             # Patient portal routes
│   └── admin.py               # Admin portal routes
│
├── templates/                  # HTML templates
│   ├── base.html              # Base template with navigation
│   ├── home.html              # Landing page
│   ├── auth/                  # Authentication templates
│   ├── doctor/                # Doctor portal templates
│   ├── patient/               # Patient portal templates
│   ├── admin/                 # Admin portal templates
│   └── errors/                # Error pages (404, 500)
│
└── static/
    ├── style.css              # Professional medical theme
    └── uploads/               # User uploads directory
```

## 📊 Database Schema

### Tables

1. **users** - Base authentication (email, password, role)
2. **doctors** - Doctor profiles and credentials
3. **patients** - Patient profiles and medical info
4. **appointments** - Booking records with medical details
5. **time_slots** - Doctor availability schedule
6. **notifications** - System notifications
7. **reviews** - Patient feedback (optional)

### Key Relationships

- Users → Doctors/Patients (one-to-one)
- Doctors → Appointments (one-to-many)
- Patients → Appointments (one-to-many)
- Doctors → Time Slots (one-to-many)

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- SQLite (CLI comes with Python)
- pip (Python package manager)

### Installation

1. **Clone/Navigate to project**

   ```bash
   cd /Users/parthkothawade/Downloads/Projects/Hospital_Management
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Database Setup**

   ```bash
   # Initialize SQLite database using the init script
   python init_db.py
   ```

4. **Configure Environment Variables**

   `DB_PATH` defaults to `hospital.db` in the project root. Override via env var if you want a different location.

5. **Run the application**

   ```bash
   python run.py
   ```

6. **Access the application**
   - Open browser: `http://127.0.0.1:8080`
   - Or: `http://localhost:8080`

## 👥 Test Accounts

### Pre-configured Users:

| Role    | Email                 | Password    | Notes                   |
| ------- | --------------------- | ----------- | ----------------------- |
| Admin   | admin@hospital.com    | admin       | Full system access      |
| Doctor  | dr.smith@hospital.com | Doctor@123  | Cardiologist (verified) |
| Patient | patient@example.com   | Patient@123 | Sample patient          |

### Or Create New Accounts:

1. **Patient**: Click "Register" → "Register as Patient"
2. **Doctor**: Click "Register" → "Register as Doctor" (requires admin verification)

## 💻 Usage Guide

### Patient Workflow

1. **Register** as a patient with personal details
2. **Login** using email and password
3. **Find Doctors** by name or specialization
4. **View Doctor Profile** to see availability
5. **Book Appointment** by selecting date and time
6. **View Appointments** in your dashboard
7. **Cancel if needed** (min. 24 hours before)
8. **View Medical Records** after consultation

### Doctor Workflow

1. **Register** with medical credentials
2. **Wait for admin verification** (or verify manually in database)
3. **Login** to access doctor portal
4. **Set Schedule** by adding time slots
5. **View Appointments** in dashboard
6. **Update Appointments** with diagnosis/prescription
7. **Mark Complete** when consultation is done
8. **Manage Profile** to update information

### Admin Workflow

1. **Login** with admin credentials
2. **Verify Doctors** in the admin panel
3. **Monitor System** activity and statistics
4. **Manage Users** as needed

### Manual Doctor Verification (If needed)

After initializing the database, the sample doctor (Dr. John Smith) is already verified. To verify additional doctors:

```bash
# Run the application and log in as admin to verify doctors through the UI
# Or manually update the database:
sqlite3 hospital.db "UPDATE doctors SET is_verified = 1 WHERE registration_number = 'MED12345';"
```

## 🔒 Security Features

1. **Password Security**

   - SHA256 hashing
   - Strength validation (8+ chars, uppercase, lowercase, number)

2. **Access Control**

   - Role-based authentication
   - Protected routes with decorators
   - Session management

3. **Input Validation**

   - Email format validation
   - Required field checking
   - SQL injection prevention (parameterized queries)

4. **Data Protection**
   - Secure session configuration
   - CSRF protection ready
   - Active account checking

## 🎨 UI/UX Features

- **Modern Design**: Clean, professional medical theme
- **Responsive Layout**: Works on desktop and mobile
- **Medical Theme**: Professional healthcare aesthetics
- **Status Indicators**: Color-coded appointment statuses
- **Empty States**: Helpful messages when no data
- **Flash Messages**: User feedback for actions

## 📝 Business Rules

### Appointment Booking

- ✅ Patients can only book during doctor's available slots
- ✅ No double-booking (conflict detection)
- ✅ Can book up to 30 days in advance
- ✅ Each slot duration: 30 minutes (configurable)

### Cancellation Policy

- ⏰ Minimum 24 hours before appointment
- 👨‍⚕️ Doctors can cancel anytime
- 🔔 Notifications sent on cancellation

### Doctor Verification

- 🔍 Admin must verify before accepting appointments
- 📋 Registration number required
- 🎓 Qualifications recorded

## 🛠️ Configuration

Edit `config.py` for:

- Session settings
- Email configuration (for notifications)
- File upload settings
- Pagination limits

```python
# Example: Change slot duration
DEFAULT_SLOT_DURATION = 45  # minutes
```

## 📈 Features Implemented

### Core Features ✅

- [x] User authentication and role management
- [x] Patient registration and profile management
- [x] Doctor registration and verification
- [x] Doctor scheduling and availability
- [x] Appointment booking with conflict detection
- [x] Medical record management
- [x] Dashboard views for all user types
- [x] Responsive web interface
- [x] Email notification system
- [x] Database schema with proper relationships

### Enhanced Features ✅

- [x] Session-based authentication
- [x] Password hashing for security
- [x] Role-based access control
- [x] Error handling and logging
- [x] Flash messaging system
- [x] Database transaction management
- [x] Input validation and sanitization

## 🐛 Troubleshooting

### Database Connection Error

```bash
# Ensure the SQLite DB file exists
ls hospital.db

# Recreate if missing/corrupted
python init_db.py

# Confirm DB path in config.py or DB_PATH env var
```

### Import Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Port Already in Use

```python
# In run.py, change port:
app.run(debug=True, port=8000)  # Use 8000 instead of 8080
```

### Template Not Found

```bash
# Ensure you're in the project root directory
cd /Users/parthkothawade/Downloads/Projects/Hospital_Management
python run.py
```

## 📄 API Documentation

### Key Routes

#### Authentication

- `GET/POST /auth/login` - Login page
- `GET/POST /auth/register/patient` - Patient registration
- `GET/POST /auth/register/doctor` - Doctor registration
- `GET /auth/logout` - Logout

#### Patient Portal

- `GET /patient/dashboard` - Patient dashboard
- `GET /patient/doctors` - Browse doctors
- `GET /patient/doctor/<id>` - Doctor profile
- `POST /patient/book-appointment` - Book appointment
- `GET /patient/appointments` - View appointments
- `POST /patient/appointment/<id>/cancel` - Cancel appointment

#### Doctor Portal

- `GET /doctor/dashboard` - Doctor dashboard
- `GET /doctor/appointments` - View appointments
- `POST /doctor/appointment/<id>/update` - Update appointment
- `GET /doctor/schedule` - Manage schedule
- `POST /doctor/schedule/add` - Add time slot

#### Admin Portal

- `GET /admin/dashboard` - Admin dashboard
- `GET /admin/doctors` - Manage doctors
- `GET /admin/patients` - Manage patients
- `POST /admin/doctor/<id>/verify` - Verify doctor

## 🤝 Contributing

This is a complete, production-ready system developed by Parth Kothawade. To customize:

1. **Add Features**: Create new routes in blueprints
2. **Modify UI**: Edit templates in `templates/`
3. **Change Styles**: Update `static/style.css`
4. **Extend Models**: Add methods in `models.py`

## 📞 Support

For issues or questions:

1. Check that all dependencies are installed: `pip install -r requirements.txt`
2. Verify database setup with `database_schema.sql`
3. Confirm configuration in `config.py`

## 🎓 Learning Resources

This project demonstrates:

- Flask application factory pattern
- Blueprint-based modular architecture
- Role-based access control
- Database relationships and models
- Form validation and security
- Session management
- RESTful routing
- Professional UI/UX design

## 📜 License

This project was created by Parth Kothawade for educational and practical purposes. Feel free to use, modify, and distribute.

## 🌟 Credits

**Developed by:** Parth Kothawade

**Technologies used:**

- Flask - Web framework
- SQLite - Database
- HTML/CSS/JavaScript - Frontend
- Python - Backend

---

**Hospital Management System - Making healthcare accessible and organized!** 🏥
