#!/usr/bin/env python3
"""
Run script for Doctor Appointment Management System
"""
from app import app

if __name__ == '__main__':
    print("=" * 60)
    print(" DOCTOR APPOINTMENT MANAGEMENT SYSTEM")
    print("=" * 60)
    print("\n Starting application...")
    print(f" Environment: development")
    print(" URL: http://127.0.0.1:8080")
    print("\n Test Accounts:")
    print(" - Admin: admin@hospital.com / admin")
    print(" - Doctor: dr.smith@hospital.com / Doctor@123")
    print(" - Patient: patient@example.com / Patient@123")
    print("\n Press CTRL+C to stop")
    print("=" * 60)
    print()

    app.run(debug=True, host='0.0.0.0', port=8080)
