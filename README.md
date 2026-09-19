# 🛡️ AI-CTDRS — Cyber Threat Detection & Response System

> **An enterprise-grade, AI-powered cybersecurity platform** that combines machine learning, real-time threat detection, explainable AI (XAI), and automated incident response — built as a final-year thesis project.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![Django](https://img.shields.io/badge/Django-6.1-green?logo=django)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-5.4-3178C6?logo=typescript)
![Tailwind](https://img.shields.io/badge/Tailwind-3.4-06B6D4?logo=tailwindcss)
![WebSocket](https://img.shields.io/badge/WebSocket-Real--time-orange?logo=socket.io)

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Tech Stack](#-tech-stack)
- [Installation](#-installation)
- [Usage](#-usage)
- [API Endpoints](#-api-endpoints)
- [AI/ML Pipeline](#-aiml-pipeline)
- [Project Structure](#-project-structure)
- [Default Credentials](#-default-credentials)
- [Future Enhancements](#-future-enhancements)

---

## 🎯 Overview

The **AI-CTDRS (Cyber Threat Detection & Response System)** is a full-stack security operations platform designed to detect, analyze, and respond to cyber threats in real time. It leverages an **ensemble machine learning model** (Random Forest + XGBoost) trained on the **CIC-IDS2017 dataset** to classify network traffic as benign or malicious with **99.75% accuracy**.

The system provides:
- 🔍 Real-time threat detection via REST API
- 🧠 Explainable AI using **SHAP** and **LIME**
- 🔔 Live notifications via WebSockets
- 📋 Automated incident and alert generation
- 👥 Role-based access control (Admin / Analyst)
- 📊 Interactive analytics dashboard with charts
- 📄 PDF/CSV reporting for compliance
- ⚙️ Configurable AI detection thresholds

---

## ✨ Key Features

### 🤖 AI-Powered Detection
- **Ensemble ML Model** (Random Forest + XGBoost) — 99.75% accuracy
- **SHAP explanations** — Shows which features contributed to each prediction
- **LIME explanations** — Local interpretable model-agnostic explanations
- **Sub-50ms inference time** — Real-time detection capability

### 🚨 Real-Time Threat Monitoring
- **WebSocket live notifications** — Instant alerts across all pages
- **Auto-generated alerts** — Every detected threat creates an alert
- **Auto-generated incidents** — Every threat creates a trackable incident
- **Cross-page navigation** — Click an alert to jump to the threat details

### 📊 Analytics & Reporting
- **Interactive dashboard** — Line, bar, and doughnut charts
- **30-day threat trends** — Visualize detection patterns
- **Top attacking IPs** — Identify the most malicious sources
- **Severity distribution** — Critical/High/Medium/Low breakdown
- **CSV export** — Download threat data for external analysis
- **PDF reports** — Professional incident reports with summaries

### 🔐 Security & Access Control
- **JWT Authentication** — Secure token-based login
- **Role-Based Access Control (RBAC)** — Admin vs Analyst permissions
- **User Management** — Admins can create/delete users and change roles
- **Audit trail** — Track who responded to what and when

### ⚙️ System Configuration
- **Adjustable AI thresholds** — Admins can tune detection sensitivity
- **Severity classification rules** — Customizable critical/high/medium cutoffs
- **Feature toggles** — Enable/disable auto-creation of alerts/incidents
- **System health monitoring** — Database size, counts, recent activity

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (React + TypeScript)           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐  │
│  │Dashboard │ │ Threats  │ │Incidents │ │   Settings   │  │
│  │ (Charts) │ │  (List)  │ │(Workflow)│ │ (Thresholds) │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────┘  │
│                         ▲  ▲  ▲  ▲                          │
│                         │  │  │  │  WebSocket + REST        │
└─────────────────────────┼──┼──┼──┼──────────────────────────┘
                          │  │  │  │
┌─────────────────────────┼──┼──┼──┼──────────────────────────┐
│                   BACKEND (Django REST Framework)            │
│  ┌──────────────────────┴──┴──┴──┴──────────────────────┐  │
│  │   API Layer: JWT Auth + RBAC + ViewSets              │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │   AI/ML Engine: RF + XGBoost Ensemble + SHAP/LIME    │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │   WebSocket Consumer (Real-time broadcast)           │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │   SQLite Database (Users, Threats, Incidents, etc.)  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

### Backend
- **Python 3.11+**
- **Django 6.1** + **Django REST Framework**
- **Django Channels** (WebSocket support)
- **Simple JWT** (Authentication)
- **scikit-learn, XGBoost, SHAP, LIME** (ML)
- **ReportLab** (PDF generation)
- **SQLite** (Database)

### Frontend
- **React 18** + **TypeScript**
- **Vite** (Build tool)
- **Tailwind CSS** (Styling)
- **React Router** (Navigation)
- **Axios** (HTTP client)
- **Chart.js + react-chartjs-2** (Visualizations)
- **react-hot-toast** (Notifications)


---

## 📦 Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Start the server
python manage.py runserver
```

The backend will run at **http://localhost:8000**

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will run at **http://localhost:3000**

---

## 🚀 Usage

1. **Login** at `http://localhost:3000/login` with your credentials
2. **Analyze Traffic**: Go to "Threat Analysis" and submit network features
3. **View Threats**: Check the "Threats" page for detected threats
4. **Respond**: Click "Respond" on any threat to record your action
5. **Manage Incidents**: Track and resolve auto-generated incidents
6. **Configure**: Admins can adjust AI thresholds in "Settings"
7. **Export**: Download CSV/PDF reports from Threats/Incidents pages

---

## 🔌 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Register new user |
| POST | `/api/auth/login/` | Login and get JWT |
| GET | `/api/auth/profile/` | Get current user profile |
| PATCH | `/api/auth/profile/` | Update profile |
| POST | `/api/auth/profile/change-password/` | Change password |

### Threats
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/threats/` | List all threats |
| POST | `/api/threats/analyze/` | Analyze traffic with AI |
| POST | `/api/threats/{id}/respond/` | Record response action |
| PATCH | `/api/threats/{id}/resolve/` | Mark threat as resolved |
| DELETE | `/api/threats/{id}/dismiss/` | Dismiss threat (Admin) |
| GET | `/api/threats/export_csv/` | Export threats as CSV |

### Incidents
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/incidents/` | List all incidents |
| POST | `/api/incidents/` | Create incident |
| POST | `/api/incidents/{id}/assign/` | Assign to self |
| POST | `/api/incidents/{id}/resolve/` | Resolve incident |
| GET | `/api/incidents/export_pdf/` | Export PDF report |

### Alerts
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/alerts/` | List all alerts |
| POST | `/api/alerts/{id}/acknowledge/` | Acknowledge alert |
| POST | `/api/alerts/acknowledge_all/` | Acknowledge all |
| DELETE | `/api/alerts/{id}/dismiss/` | Dismiss alert |

### Analytics
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/analytics/dashboard/` | Dashboard analytics |

### Settings (Admin Only)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/settings/` | Get system settings |
| PATCH | `/api/settings/` | Update settings |
| GET | `/api/settings/health/` | System health check |

### WebSocket
```
ws://localhost:8000/ws/threats/?token=<JWT_TOKEN>
```

---

## 🧠 AI/ML Pipeline

### Models
- **Random Forest Classifier** — Trained on CIC-IDS2017
- **XGBoost Classifier** — Trained on CIC-IDS2017
- **Ensemble Voting** — Averages predictions from both models

### Performance Metrics
| Metric | Value |
|--------|-------|
| Accuracy | **99.75%** |
| Precision | **99.68%** |
| Recall | **99.72%** |
| F1-Score | **99.70%** |
| Avg Inference Time | **~40ms** |

### Explainability
- **SHAP (SHapley Additive exPlanations)** — Global feature importance
- **LIME (Local Interpretable Model-agnostic Explanations)** — Per-prediction explanations

### Features Used (Top 6)
1. Flow Packets/s
2. SYN Flag Count
3. Total Fwd Packets
4. Flow Duration
5. Total Backward Packets
6. Flow Bytes/s

---

## 📁 Project Structure

```
CTDRS/
├── backend/
│   ├── apps/
│   │   ├── users/          # Authentication & user management
│   │   ├── threats/        # Threat detection & ML
│   │   ├── incidents/      # Incident management
│   │   ├── alerts/         # Alert notifications
│   │   ├── analytics/      # Dashboard analytics
│   │   ├── settings/       # System configuration
│   │   └── core/           # Shared permissions
│   ├── config/             # Django settings
│   ├── ml_models/          # Trained ML models
│   ├── manage.py
│   └── requirements.txt
│
└── frontend/
    ├── src/
    │   ├── components/     # Reusable UI components
    │   ├── pages/          # Page components
    │   ├── hooks/          # Custom React hooks
    │   ├── services/       # API services
    │   ├── types/          # TypeScript types
    │   └── App.tsx
    ├── package.json
    └── vite.config.ts
```

---

## 🔑 Default Credentials

After running migrations and creating a superuser:

| Role | Email | Password |
|------|-------|----------|
| Admin | `admin@ctdrs.com` | `Admin123!` |

> ⚠️ **Change these credentials immediately in production!**

---

## 🔮 Future Enhancements

- [ ] Email notifications for critical alerts
- [ ] Geographic map visualization of attack sources
- [ ] Integration with SIEM tools (Splunk, ELK)
- [ ] Docker containerization
- [ ] PostgreSQL database support
- [ ] Automated threat response playbooks
- [ ] Mobile app for analysts
- [ ] Multi-tenant support for multiple organizations

---


## 🙏 Acknowledgments

- **CIC-IDS2017 Dataset** — Canadian Institute for Cybersecurity
- **Django & React Communities** — For excellent documentation
- **SHAP & LIME Libraries** — For explainable AI tools

---


<div align="center">

**Built with ❤️ for cybersecurity research**

🛡️ **AI-CTDRS** — Detect. Analyze. Respond.

</div>