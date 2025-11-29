# 🚀 Hospital Management System Deployment Guide

**Created by: Parth Kothawade**

This guide provides detailed instructions for deploying the Hospital Management System to a production environment. Following these steps will allow you to host your project online and include a working link in your resume.

## 📋 Prerequisites

Before deployment, ensure you have:

1. A GitHub account
2. A hosting platform account (we'll use PythonAnywhere as an example)
3. Basic understanding of Python, Flask, and MySQL
4. The complete Hospital Management System project files

## 🌐 Option 1: Deploy to PythonAnywhere (Recommended for Beginners)

PythonAnywhere is an excellent platform for hosting Python web applications with a free tier available.

### Step 1: Prepare Your Code

1. Create a GitHub repository for your project:
   - Go to github.com and create a new repository
   - Upload all your project files to the repository
   - Ensure your repository includes:
     - `app.py`
     - `config.py`
     - `models.py`
     - `utils.py`
     - `requirements.txt`
     - `database_schema.sql`
     - All route files in `/routes/`
     - All templates in `/templates/`
     - Static files in `/static/`

### Step 2: Sign Up for PythonAnywhere

1. Visit [pythonanywhere.com](https://www.pythonanywhere.com/)
2. Sign up for a free account
3. Confirm your email address

### Step 3: Create a New Web Application

1. Log in to PythonAnywhere
2. Click on the "Web" tab
3. Click "Add a new web app"
4. Click "Next"
5. Select "Flask" as the framework
6. Choose the latest Python version (3.8 or higher)
7. Click "Next" to accept the default Flask app
8. Click "Next" again to complete setup

### Step 4: Configure Your Application

1. In the "Code" section of your web app:
   - Note the path to your code directory (e.g., `/home/yourusername/mysite/`)
2. Open a new Bash console (click "Consoles" tab, then "Bash")

3. Navigate to your home directory:

   ```bash
   cd /home/yourusername
   ```

4. Remove the default Flask app:

   ```bash
   rm -rf mysite
   ```

5. Clone your GitHub repository:

   ```bash
   git clone https://github.com/yourusername/hospital-management-system.git mysite
   ```

6. Navigate to your project directory:

   ```bash
   cd mysite
   ```

7. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Step 5: Set Up the Database (SQLite)

1. No managed DB is required—SQLite runs in-process.
2. From the Bash console, create the DB file in your project directory:
   ```bash
   sqlite3 /home/yourusername/mysite/hospital.db < /home/yourusername/mysite/database_schema.sql
   ```
3. If you move the DB file, set `DB_PATH` in your web app env vars to the new location.

### Step 6: Configure the Web Application

1. Go back to the "Web" tab
2. Click on your web app
3. In the "Code" section:

   - Set Source code path to: `/home/yourusername/mysite`
   - Set Working directory to: `/home/yourusername/mysite`

4. In the "WSGI configuration file" section, click the link to edit the file
5. Replace the contents with:

   ```python
   import sys
   import os

   path = '/home/yourusername/mysite'
   if path not in sys.path:
       sys.path.append(path)

   os.chdir(path)
   from app import app as application
   ```

6. Save the file

### Step 7: Set Environment Variables (Optional)

1. In the "Web" tab, scroll to "Environment variables"
2. Add any necessary environment variables:
   - `FLASK_ENV`: `production`
   - `SECRET_KEY`: `your_secret_key_here`

### Step 8: Reload the Application

1. Scroll to the top of the web app configuration page
2. Click the "Reload" button
3. Wait for the reload to complete

### Step 9: Test Your Application

1. Click the provided URL (e.g., `http://yourusername.pythonanywhere.com`)
2. Your Hospital Management System should be live!

## ☁️ Option 2: Deploy to Heroku

Heroku is another popular platform for hosting web applications.

### Step 1: Prepare Your Application

1. Create a `Procfile` in your project root with:

   ```
   web: gunicorn run:app
   ```

2. Update `requirements.txt` to include:

   ```
   Flask==3.1.2
   gunicorn==23.0.0
   ```

3. Modify `run.py` to work with Heroku:
   ```python
   if __name__ == '__main__':
       port = int(os.environ.get("PORT", 8080))
       app.run(host='0.0.0.0', port=port)
   ```

### Step 2: Deploy Using Git

1. Install the Heroku CLI
2. Log in to Heroku:

   ```bash
   heroku login
   ```

3. Create a new Heroku app:

   ```bash
   heroku create your-app-name
   ```

4. Set environment variables:

   ```bash
   heroku config:set FLASK_ENV=production
   ```

5. Push your code:

   ```bash
   git add .
   git commit -m "Prepare for Heroku deployment"
   git push heroku master
   ```

6. SQLite uses an on-dyno file. For platforms with ephemeral filesystems (like Heroku free tiers), consider mounting persistent storage or switching to their managed Postgres add-on.

7. If you keep SQLite, upload/seed the DB file with your deploy (e.g., include `hospital.db` built from `database_schema.sql`).

## 🐳 Option 3: Deploy with Docker (Advanced)

For a more professional deployment approach, you can containerize your application.

### Step 1: Create Dockerfile

Create a `Dockerfile` in your project root:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["python", "run.py"]
```

### Step 2: Create docker-compose.yml

Create a `docker-compose.yml` file:

```yaml
version: "3.8"

services:
  app:
    build: .
    volumes:
      - .:/app
      - ./hospital.db:/app/hospital.db
    ports:
      - "8080:8080"
    environment:
      - FLASK_ENV=production
      - DB_PATH=/app/hospital.db
      - ./hospital.db:/app/hospital.db
```

### Step 3: Build and Run

```bash
docker-compose up --build
```

## 🔧 Production Considerations

Before going live, consider these improvements:

### Security Enhancements

1. **Strong Secret Key**: Generate a strong secret key for production
2. **HTTPS**: Enable SSL/TLS encryption
3. **Database Security**: Use strong passwords and limit permissions
4. **Input Validation**: Ensure all user inputs are properly validated
5. **Rate Limiting**: Implement rate limiting to prevent abuse

### Performance Optimizations

1. **Caching**: Implement caching for frequently accessed data
2. **Database Indexes**: Ensure proper indexing for performance
3. **Static Files**: Serve static files through a CDN
4. **Load Balancing**: Use load balancers for high traffic

### Monitoring and Maintenance

1. **Logging**: Implement comprehensive logging
2. **Error Tracking**: Set up error monitoring
3. **Backups**: Regular database backups
4. **Updates**: Keep dependencies updated

## 📎 Adding to Your Resume

To showcase this project on your resume:

### Resume Entry Example:

```
Hospital Management System | Full Stack Developer
• Developed a comprehensive hospital management system using Flask, Python, and SQLite
• Implemented role-based access control for patients, doctors, and administrators
• Deployed application to PythonAnywhere with live URL: https://yourusername.pythonanywhere.com
• Features include appointment booking, doctor scheduling, medical records management
• Technologies: Python, Flask, MySQL, HTML/CSS, JavaScript
```

### GitHub Repository:

- Keep your repository public
- Include a detailed README
- Add screenshots in the repository
- Tag releases appropriately

## 🆘 Troubleshooting Common Issues

### Application Won't Start

1. Check the error log in PythonAnywhere/Web tab
2. Verify all dependencies are installed
3. Ensure database connection settings are correct
4. Check that all required environment variables are set

### Database Connection Errors

1. Verify database credentials in `config.py`
2. Ensure the database exists and is accessible
3. Check firewall settings if using external database

### Static Files Not Loading

1. Verify the static folder structure
2. Check file permissions
3. Ensure the path in templates is correct

## 📞 Support

For deployment issues:

1. Check PythonAnywhere documentation
2. Review application logs for specific error messages
3. Verify all configuration files are correctly set up

---

**Developed by Parth Kothawade**  
This deployment guide accompanies the Hospital Management System project. Follow these instructions to deploy your application and showcase your work professionally.
