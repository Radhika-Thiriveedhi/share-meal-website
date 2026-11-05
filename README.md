# ShareMeal — Surplus Food Redistribution Platform

**ShareMeal** is a realistic, production-ready surplus food redistribution web platform built with Python 3.11 and Flask. It bridges the gap between surplus food generators (restaurants, hotels, supermarkets, bakeries, event organizers) and food assistance organizations (NGOs, shelters, community kitchens) through coordinated volunteer collection logistics.

---

## 🌟 Key Features

- **Four Dedicated Role Dashboards**:
  - **Donor**: Publish food listings, set strict preservation & collection deadlines, review incoming requests, track volunteer pickup and delivery status.
  - **Receiving Organization**: Discover safe surplus food within collection windows, request required portions, track approvals, confirm receipt, and rate deliveries.
  - **Volunteer**: View verified dispatch tasks, accept pickups, get real-time donor/receiver instructions, submit delivery updates, or report safety issues.
  - **Platform Administrator**: Rigorous account verification, full donation auditing, food-safety review quarantine, real-time analytics, and automated JSON backups.
- **Strict Food Safety Workflow**:
  - Safe timeline tracking (preparation time, collection deadline, max holding temperature).
  - Allergen labeling and packaging integrity validation.
  - Safety hazard reporting mechanism with automatic donation quarantine.
- **Zero-External Database Architecture**:
  - High-performance, concurrent-safe structured JSON storage with atomic writes, automated backups, and file locking.
- **Humanized, Accessible UI/UX**:
  - Warm white/light grey surfaces, muted forest green brand identity, soft amber safety alerts, dark charcoal typography.
  - Responsive, high-contrast, zero-clutter interface designed for fast operational workflows.
  - 100% compliant with no-blue interface rule.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.11, Flask 3.0, Werkzeug (Password Hashing & Security)
- **Frontend**: Semantic HTML5, Modular CSS3 (Custom Design System), Modern Vanilla JavaScript (ES6+)
- **Storage**: Structured JSON files with FileLock & Atomic Writes
- **Testing**: Pytest automated test suite

---

## 🚀 Quick Start Guide (Windows / VS Code)

### 1. Prerequisites
Ensure Python 3.11+ and Git are installed.

### 2. Setup Virtual Environment & Install Dependencies
Open PowerShell in the project directory:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install flask filelock python-dotenv pytest
```

### 3. Run the Application
```powershell
python app.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 👥 Demo Accounts

| Role | Email | Password | Status |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin@sharemeal.org` | `Admin@123` | Verified |
| **Donor (Bistro)** | `greenbites@restaurant.com` | `Donor@123` | Verified |
| **Donor (Bakery)** | `artisano@bakery.com` | `Donor@123` | Verified |
| **Organization (Shelter)** | `hopehaven@shelter.org` | `Org@123` | Verified |
| **Organization (NGO)** | `nourishall@ngo.org` | `Org@123` | Verified |
| **Volunteer** | `alex.v@volunteer.org` | `Vol@123` | Verified |
| **Pending Donor** | `sunsetcafe@donor.com` | `Donor@123` | Verification Pending |

---

## 📜 License
Developed for social impact and sustainable food redistribution.
