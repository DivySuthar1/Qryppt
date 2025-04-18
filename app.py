from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from datetime import datetime, timedelta
from models.models import db, User
from flask_migrate import Migrate
import pyotp
from mailjet_rest import Client
from qryppt_utilities import encrypt_message, decrypt_message, generate_qr_code
from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY") or os.urandom(24)
app = Flask(__name__)
app.secret_key = SECRET_KEY
# Database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///secretmessage.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize DB and migrations
db.init_app(app)
migrate = Migrate(app, db)

# Mailjet config for sending OTP
app.config['MAILJET_API_KEY'] = os.getenv('MAILJET_API_KEY')
app.config['MAILJET_SECRET_KEY'] = os.getenv('MAILJET_SECRET_KEY')

def send_otp_email(email, otp):
    """Send OTP to user's email using Mailjet."""
    mailjet = Client(auth=(app.config['MAILJET_API_KEY'], app.config['MAILJET_SECRET_KEY']), version='v3.1')
    data = {
        'Messages': [
            {
                "From": {"Email": "divysuthar789@gmail.com", "Name": "Secret Message QR"},
                "To": [{"Email": email, "Name": "User"}],
                "Subject": "🔐 Your OTP Verification Code for Qryppt 🔐",
                "TextPart": f"Your OTP verification code is: {otp}\nThis code will expire in 10 minutes. Please use it to complete your action.",
                "HTMLPart": f"""
                    <html>
                        <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
                            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);">
                                <h2 style="color: #4CAF50; text-align: center;">🔑 OTP Verification Code</h2>
                                <p style="font-size: 18px; color: #555;">Hello 👋,</p>
                                <p style="font-size: 16px; color: #333;">To verify your identity, please use the following OTP code:</p>
                                <h3 style="text-align: center; font-size: 24px; color: #FF5733; font-weight: bold;">{otp}</h3>
                                <p style="font-size: 16px; color: #555;">This code will expire in <strong style="color: #FF5733;">10 minutes</strong>.</p>
                                <p style="font-size: 16px; color: #333;">If you didn't request this, please ignore this email.</p>
                                <p style="font-size: 14px; color: #777;">Thank you for using Qryppt! 😊</p>
                                <p style="font-size: 14px; color: #777; text-align: center;">If you have any questions, feel free to reach out to our support team.</p>
                                <hr style="border: 0; border-top: 1px solid #ddd;">
                                <footer style="text-align: center; font-size: 12px; color: #bbb;">&copy; 2025 Qryppt. All Rights Reserved.</footer>
                            </div>
                        </body>
                    </html>
                """

            }
        ]
    }
    try:
        result = mailjet.send.create(data=data)
        return result.status_code == 200
    except Exception as e:
        print(f"Mailjet error: {e}")
        return False


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone_number = request.form.get('phone_number')
        password = request.form.get('password')
        user = User.query.filter_by(phone_number=phone_number).first()

        if user and user.check_password(password):
            if not user.is_verified:
                flash("Please verify your account first.")
                return redirect(url_for('login'))

            session['user_id'] = user.id
            flash("Logged in successfully!")
            return redirect(url_for('index'))

        flash("Invalid phone number or password.")

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        phone_number = request.form.get('phone_number')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        email = request.form.get('email')

        # Input validation
        if not phone_number or not password or not confirm_password:
            flash("All fields are required.")
            return render_template('register.html')

        # Check if phone number already exists
        existing_user = User.query.filter_by(phone_number=phone_number).first()
        if existing_user:
            flash("Phone number already registered. Please use a different one.")
            return render_template('register.html')

        # Password validation
        if password != confirm_password:
            flash("Passwords do not match.")
            return render_template('register.html')

        if len(password) < 8:
            flash("Password must be at least 8 characters long.")
            return render_template('register.html')

        # Phone number format validation (basic)
        if not phone_number.isdigit() or len(phone_number) < 10:
            flash("Please enter a valid phone number.")
            return render_template('register.html')

        # Email validation (basic)
        if email and '@' not in email:
            flash("Please enter a valid email address.")
            return render_template('register.html')

        # Create new user
        try:
            new_user = User(phone_number=phone_number)
            new_user.set_password(password)

            otp_secret = pyotp.random_base32()
            totp = pyotp.TOTP(otp_secret, interval=600)
            otp = totp.now()

            new_user.set_otp(otp_secret)

            db.session.add(new_user)
            db.session.commit()

            if app.debug:
                session['dev_otp'] = otp  # Debugging only

            if email:
                success = send_otp_email(email, otp)
                if success:
                    flash("Check your email for the verification code. (Check spam folder also!)")
                else:
                    flash("Couldn't send email. OTP will show on screen if debugging.")

            session['temp_user_id'] = new_user.id
            return redirect(url_for('verify_otp'))

        except Exception as e:
            # Handle any database errors
            db.session.rollback()
            app.logger.error(f"Database error during registration: {str(e)}")
            flash("An error occurred during registration. Please try again.")

    return render_template('register.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("Logged out.")
    return redirect(url_for('index'))


@app.route('/profile')
def profile():
    if not session.get('user_id'):
        flash("Please login first.")
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if not user:
        session.pop('user_id', None)
        flash("User not found.")
        return redirect(url_for('login'))

    qr_data = f"user:{user.user_uuid}"
    qr_code = generate_qr_code(qr_data)

    return render_template('profile.html', user=user, qr_code=qr_code)


@app.route('/create-message', methods=['GET', 'POST'])
def create_message():
    if not session.get('user_id'):
        flash("Please login to create messages.")
        return redirect(url_for('login'))

    if request.method == 'POST':
        message = request.form.get('message')
        encryption_key = request.form.get('encryption_key')
        expiry_option = request.form.get('expiry_option')
        custom_expiry_date = request.form.get('custom_expiry_date')
        custom_expiry_time = request.form.get('custom_expiry_time')

        expiry_time = None
        if expiry_option == "1_hour":
            expiry_time = datetime.utcnow() + timedelta(hours=1)
        elif expiry_option == "1_day":
            expiry_time = datetime.utcnow() + timedelta(days=1)
        elif expiry_option == "1_week":
            expiry_time = datetime.utcnow() + timedelta(weeks=1)
        elif expiry_option == "custom" and custom_expiry_date:
            time_str = custom_expiry_time if custom_expiry_time else "00:00"
            try:
                expiry_time = datetime.strptime(f"{custom_expiry_date} {time_str}", "%Y-%m-%d %H:%M")
            except ValueError:
                flash("Invalid date/time format.")
                return render_template('create_message.html')

        encrypted_msg = encrypt_message(message, encryption_key, expiry_time)
        qr_code_base64 = generate_qr_code(encrypted_msg)

        return render_template('message_created.html',
                               qr_code=qr_code_base64,
                               encrypted_message=encrypted_msg,
                               expiry_time=expiry_time)

    return render_template('create_message.html')


@app.route('/decrypt-message', methods=['GET', 'POST'])
def decrypt_message_route():
    decrypted_message = None
    is_expired = False

    if request.method == 'POST':
        encrypted_data = request.form.get('encrypted_data')
        encryption_key = request.form.get('encryption_key')

        if encrypted_data and encryption_key:
            result = decrypt_message(encrypted_data, encryption_key)
            if result.startswith("This message has expired"):
                is_expired = True
            decrypted_message = result

    return render_template('decrypt_message.html',
                           decrypted_message=decrypted_message,
                           is_expired=is_expired)


@app.route('/delete-account', methods=['POST'])
def delete_account():
    if not session.get('user_id'):
        flash("Login required.")
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if not user:
        session.pop('user_id', None)
        flash("User not found.")
        return redirect(url_for('login'))

    password = request.form.get('confirm_password')
    if not user.check_password(password):
        flash("Incorrect password.")
        return redirect(url_for('profile'))

    db.session.delete(user)
    db.session.commit()
    session.pop('user_id', None)
    flash("Account deleted.")
    return redirect(url_for('index'))


@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if 'temp_user_id' not in session:
        flash("Session expired. Register again.")
        return redirect(url_for('register'))

    user = User.query.get(session['temp_user_id'])
    if not user:
        session.pop('temp_user_id', None)
        flash("User not found.")
        return redirect(url_for('register'))

    if request.method == 'POST':
        otp_code = request.form.get('otp_code')

        if not user.is_otp_valid():
            flash("OTP expired.")
            db.session.delete(user)
            db.session.commit()
            session.pop('temp_user_id', None)
            return redirect(url_for('register'))

        totp = pyotp.TOTP(user.otp_secret, interval=600)
        if totp.verify(otp_code):
            user.is_verified = True
            user.otp_secret = None
            user.otp_expiry = None
            db.session.commit()

            session.pop('temp_user_id', None)
            session['user_id'] = user.id

            qr_data = f"user:{user.user_uuid}"
            qr_code = generate_qr_code(qr_data)

            flash("Registered successfully!")
            return render_template('register_success.html', qr_code=qr_code)
        else:
            flash("Invalid OTP.")

    return render_template('verify_otp.html')


@app.cli.command("init-db")
def init_db_command():
    with app.app_context():
        db.create_all()
    print("Database initialized.")

if __name__ == '__main__':
    app.run(debug=True)
