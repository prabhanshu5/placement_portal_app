from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class AdminProfile(db.Model):
    

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


class User(db.Model):
      # IMPORTANT

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="student")

    applications = db.relationship("Application", backref="user")
    admin_profile = db.relationship("AdminProfile", backref="user", uselist=False)
    student_profile = db.relationship("StudentProfile", backref="user", uselist=False)


class StudentProfile(db.Model):
    

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    department = db.Column(db.String(100))
    cgpa = db.Column(db.Float)
    skills = db.Column(db.String(255))
    resume_link = db.Column(db.String(255))
    phone = db.Column(db.String(15))


class Company(db.Model):
    

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    website = db.Column(db.String(255))
    location = db.Column(db.String(120))

    jobs = db.relationship("Job", backref="company")


class Job(db.Model):
    

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    salary = db.Column(db.Integer)
    eligibility = db.Column(db.String(120))
    deadline = db.Column(db.DateTime)

    company_id = db.Column(db.Integer, db.ForeignKey("company.id"), nullable=False)

    applications = db.relationship("Application", backref="job")


class Application(db.Model):
    

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(50), default="applied")
    resume_link = db.Column(db.String(255))

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey("job.id"), nullable=False)


class PlacementDrive(db.Model):
   

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("company.id"), nullable=False)
    job_title = db.Column(db.String(150), nullable=False)
    job_description = db.Column(db.Text, nullable=False)
    eligibility_criteria = db.Column(db.Text)
    package = db.Column(db.String(50))
    location = db.Column(db.String(100))
    deadline = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default="Pending")