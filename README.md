# 🗂️ Job Application Management System

A Flask-powered application for job applications, statuses, companies, and AI recommended jobs based on user's skills and job requirements — all in one place.

🔗 **Live Demo:** _(https://job-application-management-system-kmoz.onrender.com/)_

---

## 📸 Screenshots

> <img width="1181" height="948" alt="image" src="https://github.com/user-attachments/assets/6027a734-e22e-4f07-90ef-c53076a43387" />


### 🏠 Dashboard
<img width="1181" height="950" alt="image" src="https://github.com/user-attachments/assets/cb9087e5-c698-4242-9f68-64e0148546ae" />
<img width="1009" height="924" alt="image" src="https://github.com/user-attachments/assets/6a0019b8-969d-4161-a1a5-ba79d3d79c2b" />



### ➕ Add New Application
<img width="1084" height="906" alt="image" src="https://github.com/user-attachments/assets/af9a6b8d-97e0-4c34-a0dd-fe7fed8d2c0a" />


### 📄 Login Page
<img width="390" height="441" alt="image" src="https://github.com/user-attachments/assets/0eca5fbb-8982-4893-923e-795954698491" />



---

## 🚀 Features

- 📝 **Track Job Applications** — company, position, status, dates.
- 🔄 **Status Updates** — Applied → Interview → Offer → Rejected.
- 🗂️ **Clean Views** — Dashboard shows all applications neatly.
- 💾 **Database Support** — Built with SQLAlchemy + Flask-Migrate.
- 🌐 **Deployment Ready** — Comes with a `Procfile` for Render/Heroku.

---

## 🛠️ Built With

- **Python 3** + **Flask**
- **WTForms**
- **Jinja2 Templates**
- **HTML5 / CSS3 / Bootstrap**
- **SQLite / PostgreSQL**
- **Flask-Migrate**

---

## 📦 Installation (Local Setup)

```bash
# 1. Clone the repository
git clone https://github.com/nnamdiindu/Job_Application_Management_System.git
cd Job_Application_Management_System

# 2. Create and activate a virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Install required packages
pip install -r requirements.txt

# 4. Create .env (example)
# SECRET_KEY=your-secret
# DATABASE_URL=sqlite:///jobs.db

# 5. Run database migrations
flask db upgrade

# 6. Start the development server
flask run
