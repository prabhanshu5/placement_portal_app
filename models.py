from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    name     = db.Column(db.String(120), nullable=False)
    email    = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role     = db.Column(db.String(20), default="student")  # student / company / admin

    student_profile = db.relationship("StudentProfile", backref="user", uselist=False)
    company_profile = db.relationship("CompanyProfile", backref="user", uselist=False)
    applications    = db.relationship("Application", backref="user")
    drives          = db.relationship("PlacementDrive", backref="company_user")


class StudentProfile(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    department  = db.Column(db.String(100))
    cgpa        = db.Column(db.Float)
    skills      = db.Column(db.String(255))
    resume_link = db.Column(db.String(255))
    phone       = db.Column(db.String(15))


class CompanyProfile(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    description = db.Column(db.Text)
    website     = db.Column(db.String(255))
    location    = db.Column(db.String(120))
    phone       = db.Column(db.String(15))


class PlacementDrive(db.Model):
    id                   = db.Column(db.Integer, primary_key=True)
    # FIX: links to the User (company) who created this drive
    company_user_id      = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    job_title            = db.Column(db.String(150), nullable=False)
    job_description      = db.Column(db.Text, nullable=False)
    eligibility_criteria = db.Column(db.Text)
    package              = db.Column(db.String(50))
    location             = db.Column(db.String(100))
    deadline             = db.Column(db.String(20), nullable=False)
    status               = db.Column(db.String(20), default="Pending")  # Pending / Approved

    applications = db.relationship("Application", backref="drive")


class Application(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    status   = db.Column(db.String(50), default="Applied")  # Applied / Approved / Rejected
    # FIX: links to PlacementDrive (not Job — we removed the separate Job model)
    user_id  = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey("placement_drive.id"), nullable=False)
