![Qryppt Logo](https://img.shields.io/badge/Qryppt-Secure_QR_Messaging-00ff00?style=for-the-badge&logo=qrcode&logoColor=white)

# Qryppt - Encrypted QR Messaging

Qryppt lets you create self-destructing encrypted messages shared via QR codes. Built with Flask and a terminal-inspired UI, this project emerged from my frustration with insecure messaging platforms.

> ⚠️ **Note:** This is a personal project built for fun. It’s fully functional, but not production-grade. Use at your own risk!

## Why Qryppt?

Ever needed to share sensitive info but worried about it lingering in chat histories or email? Qryppt creates encrypted messages that:

- Can only be decrypted with the secret key you provide
- Self-destruct after a time limit you set
- Are shareable via QR codes that leave no digital trail

Built with a minimalist "hacker aesthetic" because, let's be honest, security tools should look cool.

## Features

- **End-to-End Encryption** - AES encryption keeps messages secure
- **Customizable Expiry** - Messages self-destruct after 1 hour, 1 day, 1 week, or custom date
- **Mobile-Responsive UI** - Scan and create on any device
- **User Authentication** - Phone verification with OTP
- **Zero Message Storage** - We don't store your messages, only generate QR codes on-the-fly

## Screenshots

_Here’s a peek at the UI and vibe of Qryppt:_

![image](https://github.com/user-attachments/assets/1387fa3e-9c38-4c48-8d5f-8a3fc37d4018)
![image](https://github.com/user-attachments/assets/dfdea5cc-efc7-43fb-8229-30862cd8fecc)
![image](https://github.com/user-attachments/assets/c3c21ccd-b496-43f1-ba21-99dc4b09f158)
![image](https://github.com/user-attachments/assets/b6932886-d4ee-4430-ae42-879401e11c56)
![image](https://github.com/user-attachments/assets/5fe58689-f7f0-447c-b083-cdc440499674)

## Installation

Tested on Python 3.8+. Should work fine on most systems with minimal dependencies.

```bash
# Clone the repo
git clone https://github.com/yourusername/qryppt.git
cd qryppt

# Set up virtual env
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt

# Initialize the database
python init_db.py

# Run the app
flask run
```

## Configuration

Create a `.env` file in the root directory:

```env
FLASK_APP=app.py
MAILJET_API_KEY=your_key_here
MAILJET_SECRET_KEY=your_secret_here
SECRET_KEY=your_flask_app_secret_key
```

## License

This software is licensed under the MIT License. You’re free to use, modify, and distribute it — just give credit to the original author: **Divy Suthar** ✨  
See [LICENSE](./LICENSE) for full terms.
