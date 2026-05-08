<div align="center">

# NØ & CO.

### Premium Fashion E-Commerce Platform

<br/>

![Status](https://img.shields.io/badge/Status-Production--Ready-000000?style=for-the-badge)
![Django](https://img.shields.io/badge/Django-5.2-092E20?style=for-the-badge&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-336791?style=for-the-badge&logo=postgresql&logoColor=white)

<br/>

*Inspired by the clean, Scandinavian minimalism of H&M and ZARA — built for the modern fashion consumer.*

</div>

---

## 📖 Overview

**NØ & CO.** is a full-stack, production-grade fashion e-commerce platform built with Django 5.2. It features a sophisticated multi-variant product catalog, a complete checkout pipeline with Razorpay payment integration, a user wallet system for instant refunds, and a bespoke admin dashboard — all wrapped in a minimalist, premium UI.

---

## ✨ Features

### 🛍️ Customer-Facing

| Feature | Details |
|---|---|
| **Product Catalog** | Multi-variant support (Color × Size) with real-time stock tracking |
| **Smart Wishlist** | Dynamic "Heart" sync across all product surfaces |
| **Shopping Cart** | Persistent session-based cart with offer price calculations |
| **Checkout Flow** | Multi-step checkout with address selection and order summary |
| **Payment Gateway** | Razorpay integration with signature verification |
| **Wallet System** | Internal user wallet for refunds and direct purchases |
| **Coupon Engine** | Validated discount codes with minimum order thresholds |
| **Offer System** | Category-wise and product-wise offer pricing with countdown timers |
| **Order Management** | Order history, live status tracking, item-level cancellation & returns |
| **PDF Invoices** | Downloadable order invoices generated with xhtml2pdf |
| **Product Reviews** | Verified-purchase review and star-rating system |
| **Search & Filter** | Multi-attribute filtering by Category, Subcategory, Price, and Color |
| **Custom 404 Page** | Branded, production-ready error handling |

### ⚙️ Admin & Back-Office

| Feature | Details |
|---|---|
| **Custom Admin Dashboard** | Bespoke management interface separate from Django's default admin |
| **User Management** | View, activate, and block user accounts |
| **Product & Variant Control** | Add/edit products with integrated image cropper |
| **Cloudinary Storage** | Cloud-hosted media via `django-cloudinary-storage` |
| **Inventory Alerts** | Automated low-stock tracking at the variant level |
| **Coupon & Offer Hub** | Centralized control panel for all platform discounts |
| **Order Processing** | Update order statuses and manage partial refunds |
| **Sales Reports** | Filtered order and revenue analytics |

### 🔐 Authentication & Accounts

- Secure session-based authentication with `django-allauth`
- Google OAuth social login
- Phone number support via `phonenumbers`
- Password reset via email OTP
- Multiple saved shipping addresses with primary selection

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend Framework** | Django 5.2 |
| **Database** | PostgreSQL (via `psycopg2-binary`) |
| **Authentication** | `django-allauth` + PyJWT |
| **Payment** | Razorpay |
| **Media Storage** | Cloudinary + `django-cloudinary-storage` |
| **PDF Generation** | `xhtml2pdf` + `reportlab` |
| **Image Processing** | Pillow |
| **Environment Config** | `python-decouple` |
| **WSGI Server** | Gunicorn |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript, Tailwind CSS |

---

## 📂 Project Structure

```
no_and_co/                        # Django project root
├── no_and_co/                    # Project settings & URL config
├── accounts/                     # User authentication & profile management
├── products/                     # Product & variant logic
├── category/                     # Category & subcategory hierarchies
├── cart/                         # Shopping bag & cart sessions
├── order_management/             # Checkout flows & order processing
├── payment/                      # Razorpay payment integration
├── wallet/                       # Wallet & transaction tracking
├── coupon/                       # Discount & coupon logic
├── offers/                       # Category & product-level offers
├── wishlist/                     # Wishlist management
├── reviews/                      # Product review system
├── returns/                      # Order return & refund handling
├── admin_dashboard/              # Bespoke admin panel
├── users/                        # Extended user profiles
├── core/                         # Homepage, global views & template tags
├── utils/                        # Shared utilities & helpers
├── templates/                    # Global HTML templates & base layouts
├── static/                       # CSS, JS, and brand assets
├── media/                        # Uploaded product images (local dev)
├── manage.py
└── requirements.txt
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL
- A [Cloudinary](https://cloudinary.com/) account
- A [Razorpay](https://razorpay.com/) account (for payment processing)

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/no-and-co.git
cd no-and-co
```

### 2. Create & Activate Virtual Environment

```bash
# Create
python -m venv venv

# Activate — Windows
venv\Scripts\activate

# Activate — macOS / Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file inside the `no_and_co/` project directory and populate it:

```env
SECRET_KEY=your_django_secret_key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Database
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# Cloudinary
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# Razorpay
RAZORPAY_KEY_ID=your_key_id
RAZORPAY_KEY_SECRET=your_key_secret

# Email (for OTP)
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
```

### 5. Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create a Superuser

```bash
python manage.py createsuperuser
```

### 7. Run the Development Server

```bash
python manage.py runserver
```

Visit **http://127.0.0.1:8000** — the platform is live.

---

## 🌐 Deployment

This project is production-ready with **Gunicorn** as the WSGI server.

```bash
gunicorn no_and_co.wsgi:application --bind 0.0.0.0:8000
```

**Recommended deployment stack:** Gunicorn + Nginx + PostgreSQL on a cloud VPS (e.g., AWS EC2, DigitalOcean Droplet).

> [!IMPORTANT]
> Set `DEBUG=False` and configure `ALLOWED_HOSTS` with your actual domain before deploying to production.

---

## 📦 Key Dependencies

| Package | Purpose |
|---|---|
| `Django 5.2` | Core web framework |
| `django-allauth` | Social & standard authentication |
| `razorpay` | Payment gateway SDK |
| `cloudinary` + `django-cloudinary-storage` | Cloud media storage |
| `Pillow` | Image processing & uploads |
| `xhtml2pdf` + `reportlab` | PDF invoice generation |
| `psycopg2-binary` | PostgreSQL adapter |
| `python-decouple` | `.env` environment management |
| `gunicorn` | Production WSGI server |
| `PyJWT` | JSON Web Token handling |
| `phonenumbers` | Phone number validation |

---

<div align="center">

Developed with ❤️ for the modern fashion industry

**NØ & CO.** — *Redefining Digital Fashion.*

</div>
