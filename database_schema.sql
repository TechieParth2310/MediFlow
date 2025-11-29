-- =============================================
-- DOCTOR APPOINTMENT MANAGEMENT SYSTEM (SQLite)
-- Schema + seed data for local/dev deployments
-- =============================================
PRAGMA foreign_keys = ON;

-- Drop existing tables to allow clean re-creation
DROP TABLE IF EXISTS notifications;
DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS appointments;
DROP TABLE IF EXISTS time_slots;
DROP TABLE IF EXISTS patients;
DROP TABLE IF EXISTS doctors;
DROP TABLE IF EXISTS users;

-- =============================================
-- USERS TABLE (Base table for authentication)
-- =============================================
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('patient', 'doctor', 'admin')),
    is_active INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- DOCTORS TABLE
-- =============================================
CREATE TABLE doctors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    specialization TEXT NOT NULL,
    qualification TEXT,
    registration_number TEXT UNIQUE NOT NULL,
    phone TEXT,
    address TEXT,
    experience_years INTEGER,
    consultation_fee REAL,
    bio TEXT,
    profile_image TEXT,
    is_verified INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- =============================================
-- PATIENTS TABLE
-- =============================================
CREATE TABLE patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    date_of_birth DATE,
    gender TEXT CHECK (gender IN ('male', 'female', 'other')),
    phone TEXT,
    address TEXT,
    blood_group TEXT,
    emergency_contact TEXT,
    medical_history TEXT,
    allergies TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- =============================================
-- TIME SLOTS TABLE (Doctor's availability)
-- =============================================
CREATE TABLE time_slots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doctor_id INTEGER NOT NULL,
    day_of_week TEXT NOT NULL CHECK (day_of_week IN ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')),
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    slot_duration INTEGER DEFAULT 30, -- Duration in minutes
    is_active INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE,
    UNIQUE (doctor_id, day_of_week, start_time)
);

-- =============================================
-- APPOINTMENTS TABLE
-- =============================================
CREATE TABLE appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    doctor_id INTEGER NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    duration INTEGER DEFAULT 30, -- Duration in minutes
    status TEXT DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'confirmed', 'completed', 'cancelled', 'no_show')),
    reason_for_visit TEXT,
    symptoms TEXT,
    diagnosis TEXT,
    prescription TEXT,
    notes TEXT,
    cancelled_by TEXT CHECK (cancelled_by IN ('patient', 'doctor', 'admin')),
    cancellation_reason TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE,
    UNIQUE (doctor_id, appointment_date, appointment_time)
);

-- =============================================
-- NOTIFICATIONS TABLE
-- =============================================
CREATE TABLE notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    type TEXT DEFAULT 'system' CHECK (type IN ('appointment', 'reminder', 'cancellation', 'system')),
    is_read INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- =============================================
-- REVIEWS TABLE (Optional - for patient feedback)
-- =============================================
CREATE TABLE reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    appointment_id INTEGER NOT NULL,
    patient_id INTEGER NOT NULL,
    doctor_id INTEGER NOT NULL,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (appointment_id) REFERENCES appointments(id) ON DELETE CASCADE,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE,
    UNIQUE (appointment_id)
);

-- =============================================
-- INDEXES
-- =============================================
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_doctors_specialization ON doctors(specialization);
CREATE INDEX idx_patients_user ON patients(user_id);
CREATE INDEX idx_time_slots_doctor_day ON time_slots(doctor_id, day_of_week);
CREATE INDEX idx_appointments_patient ON appointments(patient_id);
CREATE INDEX idx_appointments_doctor ON appointments(doctor_id);
CREATE INDEX idx_appointments_date ON appointments(appointment_date);
CREATE INDEX idx_appointments_status ON appointments(status);
CREATE INDEX idx_notifications_user_read ON notifications(user_id, is_read);

-- =============================================
-- SAMPLE DATA FOR TESTING
-- =============================================

-- Insert Admin User (password: admin - SHA256 hashed)
INSERT INTO users (id, email, password, role, is_active) VALUES
(1, 'admin@hospital.com', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'admin', 1);

-- Insert Sample Doctor User (password: Doctor@123)
INSERT INTO users (id, email, password, role, is_active) VALUES
(2, 'dr.smith@hospital.com', '82a9dda829eb7f8ffe9fbe49e45d47d2dad9664fbb7adf72492e3c81ebd3e29c', 'doctor', 1);

INSERT INTO doctors (id, user_id, full_name, specialization, qualification, registration_number, phone, consultation_fee, experience_years, bio, is_verified) VALUES
(1, 2, 'Dr. John Smith', 'Cardiologist', 'MBBS, MD (Cardiology)', 'MED12345', '+1-234-567-8900', 500.00, 15, 'Experienced cardiologist with expertise in heart diseases and preventive cardiology.', 1);

-- Insert Sample Patient User (password: Patient@123)
INSERT INTO users (id, email, password, role, is_active) VALUES
(3, 'patient@example.com', '0b9c2625dc21ef05f6ad4ddf47c5f203837aa32c3eed00f7f4a4a5ed6fa1dc85', 'patient', 1);

INSERT INTO patients (id, user_id, full_name, date_of_birth, gender, phone, blood_group) VALUES
(1, 3, 'Jane Doe', '1990-05-15', 'female', '+1-234-567-8901', 'O+');

-- Insert Sample Time Slots for Doctor
INSERT INTO time_slots (doctor_id, day_of_week, start_time, end_time, slot_duration, is_active) VALUES
(1, 'Monday', '09:00:00', '12:00:00', 30, 1),
(1, 'Monday', '14:00:00', '17:00:00', 30, 1),
(1, 'Wednesday', '09:00:00', '12:00:00', 30, 1),
(1, 'Wednesday', '14:00:00', '17:00:00', 30, 1),
(1, 'Friday', '09:00:00', '12:00:00', 30, 1),
(1, 'Friday', '14:00:00', '17:00:00', 30, 1);

-- =============================================
-- VIEWS FOR COMMON QUERIES
-- =============================================

-- View for available doctor slots
CREATE VIEW available_doctors AS
SELECT 
    d.id AS doctor_id,
    d.full_name,
    d.specialization,
    d.qualification,
    d.consultation_fee,
    d.experience_years,
    u.email
FROM doctors d
JOIN users u ON d.user_id = u.id
WHERE u.is_active = 1 AND d.is_verified = 1;

-- View for appointment details
CREATE VIEW appointment_details AS
SELECT 
    a.id AS appointment_id,
    a.appointment_date,
    a.appointment_time,
    a.status,
    a.reason_for_visit,
    p.full_name AS patient_name,
    p.phone AS patient_phone,
    d.full_name AS doctor_name,
    d.specialization,
    d.consultation_fee
FROM appointments a
JOIN patients p ON a.patient_id = p.id
JOIN doctors d ON a.doctor_id = d.id;
