from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from datetime import datetime, timedelta

db = SQLAlchemy()


class User(db.Model):
    """User model for storing user-related details."""
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(15), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    is_verified = db.Column(db.Boolean, default=False)
    otp_secret = db.Column(db.String(32), nullable=True)
    otp_expiry = db.Column(db.DateTime, nullable=True)

    def set_password(self, password):
        """Set password hash for user."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if provided password matches hash."""
        return check_password_hash(self.password_hash, password)

    def set_otp(self, secret):
        """Set OTP secret and expiry."""
        self.otp_secret = secret
        self.otp_expiry = datetime.now() + timedelta(minutes=10)  # OTP expires in 10 minutes

    def is_otp_valid(self):
        """Check if OTP is still valid (not expired)."""
        if self.otp_expiry and self.otp_expiry > datetime.now():
            return True
        return False