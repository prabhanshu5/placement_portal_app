from flask import Flask, render_template, request, session, redirect, flash
from models import *

app = Flask(__name__)
app.secret_key = "your_secret_key"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///placement.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

@app.route('/')
def homepage():
    return render_template('homepage.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form.get('email')
        password = request.form.get('password')
        role     = request.form.get('role')

        user = User.query.filter_by(email=email).first()
        if not user:
            flash("No account found with that email.")
            return redirect('/login')

        if user.password != password:
            flash("Incorrect password.")
            return redirect('/login')

        if user.role != role:
            flash("Selected role does not match your account.")
            return redirect('/login')

        session['user_id'] = user.id
        session['role']    = user.role

        if role == 'admin':
            return redirect('/admin/dashboard')
        elif role == 'company':
            return redirect('/company/dashboard')
        else:
            return redirect('/student/dashboard')

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name     = request.form.get('name')
        email    = request.form.get('email')
        password = request.form.get('password')
        role     = request.form.get('role')

        if User.query.filter_by(email=email).first():
            flash("Email already registered. Please login.")
            return redirect('/login')

        new_user = User(name=name, email=email, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()

        flash("Account created! Please login.")
        return redirect('/login')
    return render_template('signup.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/student/dashboard')
def student_dashboard():
    if session.get('role') != 'student':
        return redirect('/login')
    return render_template('student/dashboard.html')

@app.route('/student/jobs')
def student_jobs():
    if session.get('role') != 'student':
        return redirect('/login')
    drives = PlacementDrive.query.filter_by(status='Approved').all()
    return render_template('student/jobs.html', drives=drives)

@app.route('/student/apply/<int:drive_id>', methods=['GET', 'POST'])
def student_apply(drive_id):
    if session.get('role') != 'student':
        return redirect('/login')

    drive = PlacementDrive.query.get_or_404(drive_id)
    user_id = session.get('user_id')
    existing = Application.query.filter_by(user_id=user_id, drive_id=drive_id).first()
    if existing:
        flash("You have already applied for this drive.")
        return redirect('/student/jobs')

    if request.method == 'POST':
        new_app = Application(
            user_id=user_id,
            drive_id=drive_id,
            status='Applied'
        )
        db.session.add(new_app)
        db.session.commit()
        flash("Application submitted successfully!")
        return redirect('/student/applications')
    return render_template('student/apply.html', drive=drive)


@app.route('/student/applications')
def student_applications():
    if session.get('role') != 'student':
        return redirect('/login')
    user_id = session.get('user_id')
    applications = Application.query.filter_by(user_id=user_id).all()
    return render_template('student/applications.html', applications=applications)


@app.route('/student/profile', methods=['GET', 'POST'])
def student_profile():
    if session.get('role') != 'student':
        return redirect('/login')

    user_id = session.get('user_id')
    profile = StudentProfile.query.filter_by(user_id=user_id).first()

    if request.method == 'POST':
        department  = request.form.get('department')
        cgpa        = request.form.get('cgpa')
        skills      = request.form.get('skills')
        resume_link = request.form.get('resume_link')
        phone       = request.form.get('phone')

        if profile:
            profile.department  = department
            profile.cgpa        = cgpa
            profile.skills      = skills
            profile.resume_link = resume_link
            profile.phone       = phone
        else:
            profile = StudentProfile(
                user_id=user_id,
                department=department,
                cgpa=cgpa,
                skills=skills,
                resume_link=resume_link,
                phone=phone
            )
            db.session.add(profile)

        db.session.commit()
        flash("Profile updated successfully!")
        return redirect('/student/profile')
    return render_template('student/profile.html', profile=profile)

@app.route('/company/dashboard')
def company_dashboard():
    if session.get('role') != 'company':
        return redirect('/login')
    return render_template('company/dashboard.html')


@app.route('/company/profile', methods=['GET', 'POST'])
def company_profile():
    if session.get('role') != 'company':
        return redirect('/login')

    user_id = session.get('user_id')
    profile = CompanyProfile.query.filter_by(user_id=user_id).first()

    if request.method == 'POST':
        description = request.form.get('description')
        website     = request.form.get('website')
        location    = request.form.get('location')
        phone       = request.form.get('phone')

        if profile:
            profile.description = description
            profile.website     = website
            profile.location    = location
            profile.phone       = phone
        else:
            profile = CompanyProfile(
                user_id=user_id,
                description=description,
                website=website,
                location=location,
                phone=phone
            )
            db.session.add(profile)

        db.session.commit()
        flash("Company profile updated successfully!")
        return redirect('/company/profile')

    return render_template('company/profile.html', profile=profile)

@app.route('/company/drive/create', methods=['GET', 'POST'])
def company_drive_create():
    if session.get('role') != 'company':
        return redirect('/login')

    if request.method == 'POST':
        new_drive = PlacementDrive(
            company_user_id      = session.get('user_id'),
            job_title            = request.form.get('job_title'),
            job_description      = request.form.get('job_description'),
            eligibility_criteria = request.form.get('eligibility_criteria'),
            deadline             = request.form.get('deadline'),
            location             = request.form.get('location'),
            package              = request.form.get('package'),
            status               = 'Pending'
        )
        db.session.add(new_drive)
        db.session.commit()
        flash("Drive created and sent for admin approval.")
        return redirect('/company/my_drives')

    return render_template('company/create_drive.html')

@app.route('/company/drive/edit/<int:drive_id>', methods=['GET', 'POST'])
def company_drive_edit(drive_id):
    if session.get('role') != 'company':
        return redirect('/login')

    #fetch the actual drive to edit
    drive = PlacementDrive.query.get_or_404(drive_id)

    if request.method == 'POST':
        drive.job_title            = request.form.get('job_title')
        drive.job_description      = request.form.get('job_description')
        drive.eligibility_criteria = request.form.get('eligibility_criteria')
        drive.deadline             = request.form.get('deadline')
        drive.location             = request.form.get('location')
        drive.package              = request.form.get('package')
        db.session.commit()
        flash("Drive updated successfully!")
        return redirect('/company/my_drives')

    return render_template('company/edit_drive.html', drive=drive)

@app.route('/company/drive/delete/<int:drive_id>', methods=['POST'])
def company_drive_delete(drive_id):
    if session.get('role') != 'company':
        return redirect('/login')
    drive = PlacementDrive.query.get_or_404(drive_id)
    db.session.delete(drive)
    db.session.commit()
    flash("Drive deleted.")
    return redirect('/company/my_drives')

@app.route('/company/my_drives')
def company_my_drives():
    if session.get('role') != 'company':
        return redirect('/login')
    drives = PlacementDrive.query.filter_by(company_user_id=session.get('user_id')).all()
    return render_template('company/my_drives.html', drives=drives)

@app.route('/company/view_applications/<int:drive_id>')
def company_view_applications(drive_id):
    if session.get('role') != 'company':
        return redirect('/login')
    applications = Application.query.filter_by(drive_id=drive_id).all()
    return render_template('company/view_applications.html', applications=applications)

@app.route('/company/application/update/<int:app_id>/<status>')
def company_update_application(app_id, status):
    if session.get('role') != 'company':
        return redirect('/login')
    application = Application.query.get_or_404(app_id)
    if status in ['approved', 'rejected']:
        application.status = status.capitalize()
        db.session.commit()
        flash(f"Application {status}.")
    return redirect(f'/company/view_applications/{application.drive_id}')

@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect('/login')
    return render_template('admin/dashboard.html')

@app.route('/admin/manage_users')
def admin_manage_users():
    if session.get('role') != 'admin':
        return redirect('/login')
    users = User.query.all()
    return render_template('admin/manage_users.html', users=users)

@app.route('/admin/manage_drives')
def admin_manage_drives():
    if session.get('role') != 'admin':
        return redirect('/login')
    drives = PlacementDrive.query.all()
    return render_template('admin/manage_drives.html', drives=drives)

@app.route('/admin/approve_drive/<int:drive_id>')
def admin_approve_drive(drive_id):
    if session.get('role') != 'admin':
        return redirect('/login')
    drive = PlacementDrive.query.get_or_404(drive_id)
    drive.status = 'Approved'
    db.session.commit()
    flash("Drive approved.")
    return redirect('/admin/manage_drives')

@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
def admin_delete_user(user_id):
    if session.get('role') != 'admin':
        return redirect('/login')
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash("User deleted.")
    return redirect('/admin/manage_users')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
