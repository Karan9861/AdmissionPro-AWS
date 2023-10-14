from flask import Flask, render_template, request, redirect, url_for, flash
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# Configure the RDS MySQL database connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://admin:project123@database-1.chq8ihup9mge.ap-south-1.rds.amazonaws.com:3306/school'
db = SQLAlchemy(app)

# Set a secret key for the application
app.secret_key = 'schoolwebsite07'

class Register(db.Model):
    __tablename__ = 'register'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String(50))
    email = db.Column(db.String(50), unique=True)
    contact_number = db.Column(db.String(10))
    password = db.Column(db.String(64))  # Assuming you'll hash and store passwords securely

    def __init__(self, full_name, email, contact_number, password):
        self.full_name = full_name
        self.email = email
        self.contact_number = contact_number
        self.password = password

class Application(db.Model):
    __tablename__ = 'applications'
    app_id = db.Column(db.String(10), primary_key=True)
    user_id = db.Column(db.String(3), nullable=False)
    fname = db.Column(db.String(50), nullable=False)
    mname = db.Column(db.String(50), nullable=True)
    lname = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    birthday = db.Column(db.Date)
    father_name = db.Column(db.String(50), nullable=False)
    father_occupation = db.Column(db.String(50), nullable=False)
    father_email = db.Column(db.String(100))
    mother_name = db.Column(db.String(50), nullable=False)
    mother_occupation = db.Column(db.String(50), nullable=False)
    mother_email = db.Column(db.String(100))
    address = db.Column(db.String(100), nullable=False)
    mobile = db.Column(db.String(10))
    religion = db.Column(db.String(20))
    custom_religion = db.Column(db.String(20), default=None)
    # Define a one-to-one relationship with the Payment model
    payment = db.relationship("Payment", uselist=False, back_populates="application")

    def __init__(self, user_id, fname, mname, lname, gender, birthday, father_name, father_occupation,
                 father_email, mother_name, mother_occupation, mother_email, address, mobile, religion, custom_religion):
        self.user_id = user_id
        self.fname = fname
        self.mname = mname
        self.lname = lname
        self.gender = gender
        self.birthday = birthday
        self.father_name = father_name
        self.father_occupation = father_occupation
        self.father_email = father_email
        self.mother_name = mother_name
        self.mother_occupation = mother_occupation
        self.mother_email = mother_email
        self.address = address
        self.mobile = mobile
        self.religion = religion
        self.custom_religion = custom_religion

class Payment(db.Model):
    __tablename__ = 'payments'
    pay_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    app_id = db.Column(db.String(10), db.ForeignKey('applications.app_id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    transaction_id = db.Column(db.String(50), nullable=False)
    contact_number = db.Column(db.String(10), nullable=False)
    transaction_date = db.Column(db.Date, nullable=False)

    # Define a relationship with the Application model
    application = db.relationship("Application", back_populates="payment")

    def __init__(self, app_id, role, transaction_id, contact_number, transaction_date):
        self.app_id = app_id
        self.role = role
        self.transaction_id = transaction_id
        self.contact_number = contact_number
        self.transaction_date = transaction_date

class AdminStatus(db.Model):
    __tablename__ = 'admin_status'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    app_id = db.Column(db.String(10), unique=True, nullable=False)
    approved = db.Column(db.Boolean)
    rejected = db.Column(db.Boolean)
    remark = db.Column(db.String(100))

    def __init__(self, app_id, approved, rejected, remark):
        self.app_id = app_id
        self.approved = approved
        self.rejected = rejected
        self.remark = remark

# Define validation functions similar to JavaScript
def validate_gender_and_dob(gender, birthday):
    return bool(gender) and bool(birthday)

def validate_mobile(mobile):
    return len(mobile) == 10 and mobile.isdigit()

def validate_transaction(transaction):
    return transaction.isdigit()

def validate_email(email):
    import re
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

def generate_app_id():
    # Query the database to find the highest existing app_id
    highest_app_id = db.session.query(Application.app_id).order_by(Application.app_id.desc()).first()

    if highest_app_id:
        # Extract the numeric part of the highest app_id and increment it
        numeric_part = int(highest_app_id[0][1:])  # Remove 'A' prefix and convert to int
        new_numeric_part = numeric_part + 1

        # Generate the new app_id with 'A' prefix and padded numeric part
        new_app_id = f'A{new_numeric_part:02}'  # Format as 'A01', 'A02', etc.
    else:
        # If no existing app_id found, start with 'A01'
        new_app_id = 'A01'

    return new_app_id

with app.app_context():
    db.create_all()

@app.route("/")
def index():
    return render_template("Home.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Get data from the registration form
        full_name = request.form.get("fullName")
        email = request.form.get("email")
        contact_number = request.form.get("contactNumber")
        password = request.form.get("password")

        # Check if the email already exists in the database
        existing_user = Register.query.filter_by(email=email).first()

        if existing_user:
            flash("Email already exists. Please use a different email.", "error")
        else:
            # Create a new user record and add it to the database
            new_user = Register(full_name=full_name, email=email, contact_number=contact_number, password=password)
            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for("login"))  # Redirect to the login page after successful registration

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Get user input from the login form
        role = request.form.get("role")
        username = request.form.get("username")
        password = request.form.get("password")

        # Check if it's the admin login
        if role == "admin" and username == "admin" and password == "admin":
            return redirect(url_for("adminstatuspage"))

        # Query the database to check if the email (username) is registered
        user = Register.query.filter_by(email=username).first()

        if user:
            # Check if the password matches (you should implement password hashing for security)
            if user.password == password:
                # Successful login, redirect based on the user's role
                if role == "admin":
                    return redirect(url_for("adminstatuspage"))
                elif role == "parent":
                    return redirect(url_for("parentstatuspage"))
                else:
                    flash("Invalid role. Please select a valid role.", "error")
            else:
                flash("Incorrect password. Please try again.", "error")
        else:
            if role == "parent":
                flash("Username is not registered. Please register.", "error")
            else:
                flash("Invalid Admin Credentials")

    return render_template("login.html")

@app.route("/login_application", methods=["GET", "POST"])
def login_application():
    if request.method == "POST":
        # Get user input from the login form
        role = request.form.get("role")
        username = request.form.get("username")
        password = request.form.get("password")

        # Query the database to check if the email (username) is registered
        user = Register.query.filter_by(email=username).first()

        if user:
            # Check if the password matches (you should implement password hashing for security)
            if user.password == password:
                # Successful login, redirect based on the user's role
                if role == "parent":
                    user_id = user.user_id
                    return render_template('application.html',user_id=user_id)
            else:
                flash("Incorrect password. Please try again.", "error")
        else:
            if role == "parent":
                flash("Username is not registered. Kindly go back and register first.", "error")

    return render_template("login_application.html")

@app.route("/application", methods=["GET", "POST"])
def application():
    if request.method == "POST":
        # Get user input from the application form
        user_id = request.form.get("user_id")
        fname = request.form.get("fname")
        mname = request.form.get("mname")
        lname = request.form.get("lname")
        gender = request.form.get("gender")
        birthday = request.form.get("birthday")
        father_name = request.form.get("fatherName")
        father_occupation = request.form.get("fatherOccupation")
        father_email = request.form.get("fatherEmail")
        mother_name = request.form.get("motherName")
        mother_occupation = request.form.get("motherOccupation")
        mother_email = request.form.get("motherEmail")
        address = request.form.get("address")
        mobile = request.form.get("mobile")
        religion = request.form.get("religion")
        custom_religion = request.form.get("customReligion")

        # Perform JavaScript-like validation on the server-side
        if (
            not fname
            or not lname
            or not gender
            or not birthday
            or not father_name
            or not father_occupation
            or not father_email
            or not mother_name
            or not mother_occupation
            or not mother_email
            or not address
            or not mobile
            or not religion
            or (religion == "Others" and not custom_religion)
            or not validate_gender_and_dob(gender, birthday)
            or not validate_mobile(mobile)
            or not validate_email(father_email)
            or not validate_email(mother_email)
        ):
            flash("Please fill in all required fields correctly before submitting.", "error")
        else:
            # Create a new Application record
            new_application = Application(user_id=user_id, fname=fname, mname=mname, lname=lname, gender=gender, birthday=birthday,
                                          father_name=father_name, father_occupation=father_occupation,
                                          father_email=father_email, mother_name=mother_name,
                                          mother_occupation=mother_occupation, mother_email=mother_email,
                                          address=address, mobile=mobile, religion=religion,
                                          custom_religion=custom_religion)
            
            # Manually generate the app_id with 'A' prefix and an incrementing number
            new_application.app_id = generate_app_id()

            # Add the new application record to the database
            db.session.add(new_application)
            db.session.commit()
            return redirect(url_for("payment"))  # Redirect to the parent status page

    return render_template("application.html")


@app.route("/payment", methods=["GET", "POST"])
def payment():
    if request.method == "POST":
        # Get data from the payment form
        role = request.form.get("paymentMode")
        transaction_id = request.form.get("transactionId")
        contact_number = request.form.get("contactNumber")
        transaction_date = request.form.get("transactionDate")

        # Get the latest app_id from the applications table
        latest_application = Application.query.order_by(Application.app_id.desc()).first()
        
        if latest_application:
            app_id = latest_application.app_id

            # Perform JavaScript-like validation on the server-side
            if (
                not role
                or not validate_transaction(transaction_id)
                or not validate_mobile(contact_number)
                or not transaction_date
            ):
                flash("Please fill in all required fields correctly before submitting.", "error")
            else:
                # Create a new payment record and link it to the application
                new_payment = Payment(
                    app_id=app_id,
                    role=role,
                    transaction_id=transaction_id,
                    contact_number=contact_number,
                    transaction_date=transaction_date
                )

                db.session.add(new_payment)
                db.session.commit()

                return render_template('payment.html', app_id=app_id, payment_status=True)
            
    return render_template("payment.html",payment_status=False)

@app.route('/adminstatuspage', methods=['GET', 'POST'])
def adminstatuspage():
    # Get all unique app_id values from the Application table
    app_ids = [result[0] for result in db.session.query(Application.app_id).distinct()]

    # Populate admin_status_data with default values
    admin_status_data = [{'app_id': app_id, 'approved': False, 'rejected': False, 'remark': ''} for app_id in app_ids]

    if request.method == 'POST':
        app_id = request.form.get('app_id')
        
        # Get the selected radio button value
        status = request.form.get(f'status_{app_id}')

        # Update the corresponding record
        record = next((data for data in admin_status_data if data['app_id'] == app_id), None)
        if record:
            if status == 'approved':
                record['approved'] = True
                record['rejected'] = False
            elif status == 'rejected':
                record['approved'] = False
                record['rejected'] = True

            remark = request.form.get('remark')
            record['remark'] = remark

            # Check if a record with the same app_id exists in the AdminStatus table
            existing_record = AdminStatus.query.filter_by(app_id=app_id).first()

            if existing_record:
                # Update the existing record in the database
                existing_record.approved = record['approved']
                existing_record.rejected = record['rejected']
                existing_record.remark = remark
            else:
                # Create a new record and store it in the AdminStatus table
                admin_status_record = AdminStatus(
                    app_id=app_id,
                    approved=record['approved'],
                    rejected=record['rejected'],
                    remark=remark
                )
                db.session.add(admin_status_record)

            db.session.commit()

    return render_template('adminstatuspage.html', admin_status_data=admin_status_data)


@app.route('/parentstatuspage', methods=['GET', 'POST'])
def parentstatuspage():
    if request.method == 'POST':
        try:
            application_number = request.form.get('applicationNumber')
            # Check if a record with the provided application number exists in the AdminStatus table
            admin_status_record = AdminStatus.query.filter_by(app_id=application_number).first()

            if admin_status_record:
                if admin_status_record.approved == 1:
                    status = "Accepted"
                elif admin_status_record.rejected == 1:
                    status = "Rejected"
                else:
                    status = "Pending"
                feedback = admin_status_record.remark if admin_status_record.remark else "No feedback provided."
            else:
                status = "No status found for the provided application number."
                feedback = "No feedback available."
        
        except Exception as e:
            status = "Error: Kindly enter a valid application number."
            feedback = "No feedback available."

        return render_template('parentstatuspage.html', status=status, feedback=feedback, app_status=True)

    return render_template('parentstatuspage.html', app_status=False)


@app.route("/investiture_ceremony")
def investiture_ceremony():
    return render_template("investiture_ceremony.html")

@app.route("/Gallery")
def Gallery():
    return render_template("Gallery.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/facilities")
def facilities():
    return render_template("facilities.html")

@app.route("/faculties")
def faculties():
    return render_template("faculties.html")

@app.route("/teachers_day")
def teachers_day():
    return render_template("teachers_day.html")

@app.route("/sports_day")
def sports_day():
    return render_template("sports_day.html")

@app.route("/childrens_day")
def childrens_day():
    return render_template("childrens_day.html")

@app.route("/announcement")
def announcement():
    return render_template("announcement.html")

@app.route("/Admission")
def Admission():
    return render_template("Admission.html")

@app.route("/About")
def About():
    return render_template("About.html")

if __name__ == '__main__':
    app.run(debug=True)

    