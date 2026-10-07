# 🚨 Online Crime Reporting System
> Python 3.11.9 · Django 4.2.7 · SQLite

A complete Django web application for citizens to file, track, and manage crime reports online, with a staff admin panel for investigators.

---

## 📁 Project Structure

```
crime_reporting/
├── manage.py
├── requirements.txt
├── db.sqlite3                    ← auto-created after migrations
├── media/evidence/               ← uploaded evidence images
├── core/                         ← Project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── reports/                      ← Main application
    ├── models.py                 ← CrimeReport model
    ├── forms.py                  ← Register, Login, Report, StatusUpdate forms
    ├── views.py                  ← All views
    ├── urls.py                   ← URL routing
    ├── admin.py                  ← Django admin config
    └── templates/reports/
        ├── base.html             ← Shared layout & navbar
        ├── login.html
        ├── register.html
        ├── dashboard.html
        ├── report_form.html      ← Create & Edit report
        ├── report_list.html
        ├── report_detail.html
        ├── report_confirm_delete.html
        ├── track.html            ← Public tracking page
        └── admin_panel.html      ← Staff-only panel
```

---

## 🚀 Setup & Run

### 1. Create & activate virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Create Migrations
```bash
python manage.py makemigrations reports
```

### 4. Run migrations
```bash
python manage.py migrate
```

### 5. Create a superuser (admin/staff access)
```bash
python manage.py createsuperuser
```

### 5. Start the development server
```bash
python manage.py runserver
```

---

## 🌐 Pages & URLs

| Page                  | URL                              | Access            |
|-----------------------|----------------------------------|-------------------|
| Home (redirect)       | `/`                              | Public            |
| Register              | `/register/`                     | Public            |
| Login                 | `/login/`                        | Public            |
| Logout                | `/logout/` (POST)                | Logged in         |
| Dashboard             | `/dashboard/`                    | Logged in         |
| File New Report       | `/reports/new/`                  | Logged in         |
| Tracking Number page  | `/reports/submitted/<uuid>/`     | Logged in         |
| Track Report          | `/track/`                        | **Public**        |
| Police Login          | `/police/login/`                 | Public            |
| Police Dashboard      | `/police/dashboard/`             | Police / Admin    |
| All Reports           | `/police/reports/`               | Police / Admin    |
| Register Officer      | `/police/register/`              | Admin only        |
| Django Admin          | `/admin/`                        | Superuser (Admin) |

Citizens can only **file a report** and **track a report**. After filing, they are shown a tracking number.
The Admin (superuser) can access everything: Django admin, officer registration and the police portal pages.

---------------------|------------------------------|--------------|
| Home (redirect)     | `/`                          | Public       |
| Register            | `/register/`                 | Public       |
| Login               | `/login/`                    | Public       |
| Logout              | `/logout/` (POST)            | Logged in    |
| Dashboard           | `/dashboard/`                | Logged in    |
| File New Report     | `/reports/new/`              | Logged in    |
| My Reports          | `/reports/`                  | Logged in    |
| Report Detail       | `/reports/<id>/`             | Owner/Staff  |
| Edit Report         | `/reports/<id>/edit/`        | Owner only   |
| Delete Report       | `/reports/<id>/delete/`      | Owner only   |
| Track Report        | `/track/`                    | **Public**   |
| Staff Admin Panel   | `/admin-panel/`              | Staff only   |
| Django Admin        | `/admin/`                    | Superuser    |

---

## ✨ Features

### Citizen Features
- ✅ User Registration & Login
- ✅ File crime reports with 10 crime categories
- ✅ Optional anonymous reporting
- ✅ Upload evidence images
- ✅ Provide suspect name & description
- ✅ Edit reports (pending status only)
- ✅ Delete own reports
- ✅ Search & filter reports by status/type
- ✅ Public report tracking by UUID (no login needed)
- ✅ Personal dashboard with stats

### Staff / Investigator Features
- ✅ Admin panel with all reports
- ✅ Update report status (Pending → Investigating → Resolved → Closed)
- ✅ Set priority (Low / Medium / High / Critical)
- ✅ Add investigation notes visible to reporter
- ✅ Filter & search all reports
- ✅ Full Django admin at `/admin/`

### Crime Categories
- 🔓 Theft / Burglary
- 👊 Assault / Physical Violence
- 💻 Cybercrime / Online Fraud
- ⚠️  Harassment / Stalking
- 🏚️  Vandalism / Property Damage
- 💊 Drug Related
- 💳 Financial Fraud / Scam
- 🔍 Missing Person
- 🚗 Road Accident
- 📋 Other

---

## 🔑 Django Concepts Used

| Concept | Where Used |
|---------|-----------|
| `Model` with UUID field | `reports/models.py` |
| `UserCreationForm` / `AuthenticationForm` | `reports/forms.py` |
| `ModelForm` | `CrimeReportForm`, `StatusUpdateForm` |
| `@login_required` | All protected views |
| `is_staff` check | Admin panel & status update |
| `ImageField` + `MEDIA_ROOT` | Evidence uploads |
| `django.contrib.messages` | Flash notifications |
| Template inheritance | `base.html` → all pages |
| `Q` objects | Search filtering |
| `get_object_or_404` | Safe object lookup |
