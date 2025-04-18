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

![image](https://github.com/user-attachments/assets/f10b39dc-4da7-459a-ae99-5211f2cd4f55)
![image](https://github.com/user-attachments/assets/538702c9-2769-4c8d-826f-75230296a73c)
![image](https://github.com/user-attachments/assets/7110421e-db44-4a68-b86c-43848d54f047)
![image](https://github.com/user-attachments/assets/6192df21-b498-4ddf-b824-6bc5f73f9c68)
![image](https://github.com/user-attachments/assets/99b791da-376b-4bec-bf03-2c2c1b384fb1)
![image](https://github.com/user-attachments/assets/5e32e10d-45de-4d70-8f4a-9615ded0a1df)

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
