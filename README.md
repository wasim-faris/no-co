# NØ & CO.
### H&M Inspired Modern Fashion Ecommerce Platform
---

<div align="center">
  <img src="https://img.shields.io/badge/Status-Production--Ready-black?style=for-the-badge" alt="Status">
  <img src="https://img.shields.io/badge/UI/UX-Minimalist-black?style=for-the-badge" alt="UI/UX">
  <img src="https://img.shields.io/badge/Architecture-MVC-black?style=for-the-badge" alt="Architecture">
</div>

<br />

NØ & CO is a premium fashion e-commerce destination built for the modern consumer. Inspired by the clean, Scandinavian minimalist aesthetic of industry leaders like H&M and ZARA, this platform delivers a seamless, high-performance shopping experience. From a sophisticated variant management system to a robust checkout flow, every detail is engineered for scalability and aesthetic excellence.

---

## 🛠️ Tech Stack

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.x-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Django-4.x-092E20?style=flat-square&logo=django&logoColor=white" alt="Django">
  <img src="https://img.shields.io/badge/PostgreSQL-Data-336791?style=flat-square&logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/HTML5-Structure-E34F26?style=flat-square&logo=html5&logoColor=white" alt="HTML5">
  <img src="https://img.shields.io/badge/CSS3-Design-1572B6?style=flat-square&logo=css3&logoColor=white" alt="CSS3">
  <img src="https://img.shields.io/badge/JavaScript-Logic-F7DF1E?style=flat-square&logo=javascript&logoColor=black" alt="JavaScript">
  <img src="https://img.shields.io/badge/Tailwind-Styling-06B6D4?style=flat-square&logo=tailwind-css&logoColor=white" alt="Tailwind">
  <img src="https://img.shields.io/badge/Git-Version_Control-F05032?style=flat-square&logo=git&logoColor=white" alt="Git">
</div>

---

## 💎 Key Features

### 🛍️ Customer Experience
- **Premium UI/UX**: Minimalist fashion-forward design with responsive layouts.
- **Advanced Product Catalog**: Multi-variant support (Color/Size) with real-time stock tracking.
- **Smart Wishlist**: Dynamic "Heart" sync across the entire platform.
- **Secure Checkout**: Streamlined multi-step checkout with wallet and Razorpay integration.
- **Offer System**: Category-wise and product-wise offer pricing with countdown timers.
- **Coupon Engine**: Robust coupon validation system for discounted shopping.
- **Order Management**: Comprehensive order history, status tracking, and easy returns/cancellations.

### 🛡️ Core Infrastructure
- **Authentication**: Secure JWT/Session based auth with password recovery.
- **Wallet System**: Integrated user wallet for instant refunds and internal transactions.
- **Address Management**: Multiple shipping address support with primary selection.
- **Search & Filtering**: High-performance multi-attribute filtering (Category, Subcategory, Price, Color).

### ⚙️ Administrative Control
- **Custom Admin Dashboard**: Bespoke management interface for products, orders, and users.
- **Image Processing**: Integrated image cropper for standardized product photography.
- **Stock Control**: Automated inventory alerts and variant-level management.
- **Coupon & Offer Management**: Centralized hub for controlling platform-wide discounts.

---

## 🚀 Installation & Setup

Follow these steps to get the project running locally:

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/no-and-co.git
cd no-and-co
```

### 2. Environment Setup
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Run Server
```bash
python manage.py runserver
```

---

## 📂 Project Structure

```text
no_and_co/
├── accounts/          # User authentication & Profile management
├── products/          # Product & Variant logic
├── category/          # Category & Subcategory hierarchies
├── cart/              # Shopping bag & Cart sessions
├── order_management/  # Checkout flows & Order processing
├── wallet/            # Wallet & Transaction tracking
├── coupon/            # Discount & Coupon logic
├── core/              # Homepage & Global views
├── templates/         # UI Components & Page layouts
└── static/            # Stylesheets, Scripts, and Brand assets
```

---

## 📸 Screenshots

| Homepage | Product Details |
| :---: | :---: |
| ![Homepage Placeholder](https://placehold.co/600x400?text=Minimalist+Homepage+UI) | ![PDP Placeholder](https://placehold.co/600x400?text=Premium+Product+Page) |

| Cart & Bag | Admin Dashboard |
| :---: | :---: |
| ![Cart Placeholder](https://placehold.co/600x400?text=Streamlined+Checkout) | ![Admin Placeholder](https://placehold.co/600x400?text=Powerful+Admin+Dashboard) |

---

<div align="center">
  <p>Developed with ❤️ for the Modern Fashion Industry</p>
  <p><strong>NØ & CO.</strong> — Redefining Digital Fashion.</p>
</div>
