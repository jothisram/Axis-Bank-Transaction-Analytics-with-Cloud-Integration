# Axis Bank Transaction Analytics with Cloud Integration

A full-stack enterprise banking analytics platform built with **FastAPI**, **Streamlit**, **PostgreSQL**, and **AWS** (S3, Lambda, RDS).

## 🏦 Features

### Portals

- **Customer Portal** — View balance, transactions, spending analytics, balance trends, cash flow, and a financial calculator (EMI / Savings / Compound Interest)
- **Branch Management Portal** — Monitor branch performance, customer portfolios, monthly activity, category analysis, and top performers
- **Admin Control Panel** — Full system oversight with TOTP MFA, manager approvals, branch comparison, global analytics, and customer lookup

### Security

- JWT Authentication for all portals
- TOTP Multi-Factor Authentication for Admin access (Google Authenticator / Authy)
- bcrypt password hashing

### Cloud Integration

- **AWS S3** — Customer statement uploads
- **AWS Lambda** — Statement processing and data extraction
- **AWS RDS (PostgreSQL)** — Production database

## 🛠️ Tech Stack

| Layer    | Technology                                 |
| -------- | ------------------------------------------ |
| Frontend | Streamlit, Plotly                          |
| Backend  | FastAPI, SQLAlchemy                        |
| Database | PostgreSQL (local) / AWS RDS               |
| Auth     | JWT + TOTP MFA (pyotp)                     |
| Cloud    | AWS S3, Lambda, RDS                        |
| Styling  | Custom CSS, Inter font, Axis Bank branding |

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL
- AWS account (optional, for cloud features)

### Installation

```bash
# Clone the repository
git clone https://github.com/jothisram/Axis-Bank-Transaction-Analytics-with-Cloud-Integration.git
cd Axis-Bank-Transaction-Analytics-with-Cloud-Integration

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirement.txt
```

### Configuration

Create a `.env` file in the root directory:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/axis_db
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-admin-password
```

### Running the Application

```bash
# Start the FastAPI backend
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Start the Streamlit frontend (in a new terminal)
python -m streamlit run frontend/app.py --server.port 8501
```

Open your browser at `http://localhost:8501`

## 📁 Project Structure

```
axis_dashboard/
├── backend/
│   ├── main.py          # FastAPI app entry point
│   ├── auth.py          # Authentication routes (JWT + TOTP)
│   ├── models.py        # SQLAlchemy models
│   └── routers/         # API route handlers
├── frontend/
│   ├── app.py           # Streamlit main app (landing page)
│   ├── pages/
│   │   ├── 1_Customer.py    # Customer dashboard
│   │   ├── 2_Management.py  # Branch management dashboard
│   │   └── 3_Admin.py       # Admin control panel
│   └── utils/
│       ├── styles.py    # CSS / styling utilities
│       └── api.py       # API helper functions
├── requirement.txt
└── .env                 # (not committed — see Configuration)
```

## 📸 Screenshots

| Page                 | Description                                             |
| -------------------- | ------------------------------------------------------- |
| Landing              | Portal selection with Customer, Management, Admin cards |
| Customer Dashboard   | Balance, transactions, spending charts                  |
| Management Dashboard | Branch KPIs, customer list, category analysis           |
| Admin Panel          | System overview, manager approvals, branch comparison   |

## 📄 License

This project is for educational and demonstration purposes.

---

**Built with ❤️ for Axis Bank Analytics**
