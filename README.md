# Quiz Master 🧠📚

A **multi-user quiz application** built using **Flask** that enables administrators to create and manage quizzes while allowing users to attempt quizzes and track their performance.  
This project was developed as the **Final Project for Modern Application Development – I (MAD-I)**.

---

## 🚀 Project Overview

**Quiz Master** is an exam preparation platform designed for multiple subjects and courses.  
The application supports **role-based access**, ensuring clear separation of responsibilities between administrators and users.

- Administrators manage the complete quiz lifecycle
- Users attempt quizzes and monitor their progress
- Secure authentication and structured database design ensure reliability and scalability

---

## 🛠️ Tech Stack

### Backend
- Flask
- Flask-SQLAlchemy
- SQLite (course-mandated database)
- Werkzeug Security
- python-dotenv

### Frontend
- HTML5
- CSS3
- Bootstrap
- Jinja2

### Visualization & Utilities
- JavaScript
- Chart.js (for score and performance visualization)
- CSV module
- OS module

---

## ✨ Features

### 👤 User Features
- User registration and login
- Attempt quizzes across different subjects and chapters
- View quiz scores and progress history
- Performance visualization using charts

### 🛡️ Admin Features
- Admin login
- Create, update, and delete:
  - Subjects
  - Chapters
  - Quizzes
  - Questions
- Monitor user participation and quiz engagement

### 🔐 Security Features
- Password hashing using Werkzeug
- Sensitive credentials managed through environment variables

---

## 🧱 Application Architecture

quiz-master/
│
├── app.py
├── routes.py # Routing and business logic
├── models.py # SQLAlchemy database models
├── templates/ # Jinja2 HTML templates
├── static/
│ ├── css/
│ └── js/
├── instance/
│ └── database.sqlite3
├── .env
├── requirements.txt
└── README.md



---

## 🗄️ Database Schema

The database is designed using relational principles and includes the following tables:

- **Users** – Stores user credentials and roles
- **Subjects** – Subject-level information
- **Chapters** – Linked to subjects
- **Quizzes** – Linked to chapters
- **Questions** – Linked to quizzes
- **Scores** – Tracks quiz attempts and results

### Design Highlights
- Primary and foreign keys for data integrity
- Cascade delete for dependent records
- Modular and scalable structure suitable for multi-user systems

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/23f3001900/quiz-master.git
cd quiz-master
```
### 2️⃣ Create and Activate Virtual Environment
```bash
python -m venv venv
source venv/bin/activate     # Windows: venv\Scripts\activate
```
### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```
### 4️⃣ Setup Environment Variables

Create a .env file in the project root:
```env
SECRET_KEY=your_secret_key
DATABASE_URI=sqlite:///instance/database.sqlite3
```

### 5️⃣ Run the Application
```bash
python app.py
```

The application will be available at:
```
http://127.0.0.1:5000/
```



### 📜 License

This project is developed strictly for academic purposes as part of IIT Madras coursework.
