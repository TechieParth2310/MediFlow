#!/usr/bin/env python3
"""
Database initialization script for Hospital Management System
Creates and initializes the SQLite database with schema and seed data
"""

import sqlite3
import os
from config import config


def init_database():
    """Initialize the SQLite database with schema and seed data"""
    # Get the development configuration
    app_config = config['development']

    # Get database path from config
    db_path = getattr(app_config, "DB_PATH", "hospital.db")

    print(f"Initializing database at: {db_path}")

    # Remove existing database if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
        print("Removed existing database")

    # Create database connection
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Enable foreign key constraints
    cursor.execute("PRAGMA foreign_keys = ON")

    print("Creating database schema...")

    # Read and execute the schema file
    schema_file = os.path.join(
        os.path.dirname(__file__), 'database_schema.sql')

    if not os.path.exists(schema_file):
        print(f"Error: Schema file not found at {schema_file}")
        return False

    with open(schema_file, 'r') as f:
        schema_sql = f.read()

    # Split the schema into individual statements and execute them
    # We need to handle this carefully to ensure tables are created before indexes
    statements = []
    current_statement = ""

    for line in schema_sql.split('\n'):
        line = line.strip()
        if line.startswith('--') or not line:
            continue

        current_statement += line + "\n"

        if line.endswith(';'):
            statements.append(current_statement.strip())
            current_statement = ""

    # Execute table creation statements first, then indexes
    table_statements = [s for s in statements if s.startswith(
        ('CREATE TABLE', 'INSERT'))]
    index_statements = [s for s in statements if s.startswith('CREATE INDEX')]
    view_statements = [s for s in statements if s.startswith('CREATE VIEW')]
    pragma_statements = [s for s in statements if s.startswith('PRAGMA')]
    drop_statements = [s for s in statements if s.startswith('DROP')]

    # Order: PRAGMA, DROP, CREATE TABLE, INSERT, CREATE INDEX, CREATE VIEW
    ordered_statements = pragma_statements + drop_statements + \
        table_statements + index_statements + view_statements

    for statement in ordered_statements:
        if statement and not statement.startswith('--'):
            try:
                print(f"Executing: {statement[:50]}...")
                cursor.execute(statement)
            except sqlite3.Error as e:
                print(f"Error executing statement: {statement[:50]}...")
                print(f"Error: {e}")
                conn.rollback()
                return False

    conn.commit()
    conn.close()

    print("Database initialized successfully!")
    print("\nTest accounts available:")
    print("- Admin: admin@hospital.com / admin")
    print("- Doctor: dr.smith@hospital.com / Doctor@123")
    print("- Patient: patient@example.com / Patient@123")

    return True


if __name__ == '__main__':
    init_database()
