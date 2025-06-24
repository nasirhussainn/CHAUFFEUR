🚗 CHAUFFEUR – Backend API
CHAUFFEUR is a modular and scalable Django-based backend for managing users, drivers, ride requests, and other transportation operations.

🚀 Features
✅ Modular Django app architecture

🔐 JWT-based authentication with DRF

🛠️ PostgreSQL database integration

🔧 Environment-specific settings using django-environ

🧪 Unit test-ready with Django’s built-in test framework

📁 Clean .venv virtual environment setup

🏗️ Tech Stack
Framework: Django + Django REST Framework

Database: PostgreSQL

Authentication: JWT (djangorestframework-simplejwt)

Environment Config: .env via django-environ

Testing: Django TestCase / pytest (optional)

📁 Project Structure
bash
Copy
Edit
CHAUFFEUR/
├── api/                     # Main app logic (models, views, etc.)
├── chauffeur_backend/       # Project core
│   └── settings/            # base.py, dev.py, prod.py
├── .env                     # Secret keys and DB info (ignored in git)
├── .venv/                   # Python virtual env (ignored in git)
├── manage.py
├── requirements.txt
└── README.md
⚙️ Setup Instructions
1. Clone the Repository
bash
Copy
Edit
git clone https://github.com/your-username/CHAUFFEUR.git
cd CHAUFFEUR
2. Create and Activate Virtual Environment
bash
Copy
Edit
python -m venv .venv
# On Windows
.venv\Scripts\activate
# On macOS/Linux
source .venv/bin/activate
3. Install Dependencies
bash
Copy
Edit
pip install -r requirements.txt
4. Configure Environment
Create a .env file in the root:

ini
Copy
Edit
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=chauffeur_db
DB_USER=your_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
5. Run Migrations
bash
Copy
Edit
python manage.py migrate --settings=chauffeur_backend.settings.dev
6. Run Server
bash
Copy
Edit
python manage.py runserver --settings=chauffeur_backend.settings.dev
🔐 Authentication
This project uses JWT Authentication.

POST /api/v1/token/ → Get access and refresh tokens

POST /api/v1/token/refresh/ → Get new access token

🧪 Running Tests
bash
Copy
Edit
python manage.py test --settings=chauffeur_backend.settings.dev
🤝 Contributing
Fork this repository

Create your feature branch: git checkout -b feature-name

Commit changes: git commit -m "Add feature"

Push to branch: git push origin feature-name

Submit a pull request

📄 License
MIT License
