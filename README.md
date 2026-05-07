<!-- # NØ & CO.
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
</div> -->
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NØ & CO. — Modern Fashion Platform</title>
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --ink: #0a0a0a;
    --paper: #f5f2ee;
    --accent: #c8ff00;
    --mid: #1a1a1a;
    --muted: #6b6b6b;
    --border: rgba(10,10,10,0.12);
    --tag-bg: rgba(10,10,10,0.06);
  }

  html { scroll-behavior: smooth; }

  body {
    background: var(--ink);
    color: var(--paper);
    font-family: 'DM Sans', sans-serif;
    font-weight: 300;
    overflow-x: hidden;
    line-height: 1.6;
  }

  /* ── NOISE OVERLAY ── */
  body::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E");
    pointer-events: none;
    z-index: 9999;
    opacity: 0.6;
  }

  /* ── PROGRESS BAR ── */
  #progress {
    position: fixed;
    top: 0; left: 0;
    height: 2px;
    background: var(--accent);
    width: 0%;
    z-index: 1000;
    transition: width 0.1s;
  }

  /* ── NAV ── */
  nav {
    position: fixed;
    top: 0; left: 0; right: 0;
    padding: 20px 48px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    z-index: 100;
    mix-blend-mode: difference;
  }

  .nav-logo {
    font-family: 'Bebas Neue', cursive;
    font-size: 22px;
    letter-spacing: 0.12em;
    color: white;
    text-decoration: none;
  }

  .nav-badge {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.08em;
    color: rgba(255,255,255,0.5);
    text-transform: uppercase;
  }

  /* ── HERO ── */
  .hero {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 120px 48px 80px;
    position: relative;
    overflow: hidden;
  }

  .hero-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 32px;
    opacity: 0;
    transform: translateY(16px);
    animation: fadeUp 0.8s 0.2s forwards;
  }

  .hero-title {
    font-family: 'Bebas Neue', cursive;
    font-size: clamp(72px, 14vw, 180px);
    line-height: 0.9;
    letter-spacing: -0.01em;
    color: var(--paper);
    margin-bottom: 40px;
    opacity: 0;
    transform: translateY(24px);
    animation: fadeUp 0.9s 0.35s forwards;
  }

  .hero-title .stroke {
    -webkit-text-stroke: 1px var(--paper);
    color: transparent;
  }

  .hero-sub {
    max-width: 480px;
    font-size: 15px;
    color: rgba(245,242,238,0.55);
    line-height: 1.7;
    margin-bottom: 56px;
    opacity: 0;
    transform: translateY(16px);
    animation: fadeUp 0.8s 0.5s forwards;
  }

  .hero-cta-row {
    display: flex;
    align-items: center;
    gap: 32px;
    opacity: 0;
    transform: translateY(16px);
    animation: fadeUp 0.8s 0.65s forwards;
  }

  .btn-primary {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    background: var(--accent);
    color: var(--ink);
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
    font-size: 13px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    padding: 14px 28px;
    text-decoration: none;
    transition: transform 0.2s, box-shadow 0.2s;
  }

  .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 8px 32px rgba(200,255,0,0.3); }

  .btn-ghost {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: rgba(245,242,238,0.4);
    text-decoration: none;
    border-bottom: 1px solid rgba(245,242,238,0.15);
    padding-bottom: 2px;
    transition: color 0.2s, border-color 0.2s;
  }
  .btn-ghost:hover { color: var(--paper); border-color: var(--paper); }

  /* ── MARQUEE ── */
  .marquee-section {
    border-top: 1px solid rgba(245,242,238,0.08);
    border-bottom: 1px solid rgba(245,242,238,0.08);
    padding: 18px 0;
    overflow: hidden;
    margin: 0 0 120px;
  }

  .marquee-track {
    display: flex;
    gap: 0;
    animation: marquee 20s linear infinite;
    white-space: nowrap;
  }

  .marquee-item {
    font-family: 'Bebas Neue', cursive;
    font-size: 18px;
    letter-spacing: 0.15em;
    color: rgba(245,242,238,0.2);
    padding: 0 48px;
    flex-shrink: 0;
  }

  .marquee-item.accent { color: var(--accent); }

  @keyframes marquee {
    from { transform: translateX(0); }
    to { transform: translateX(-50%); }
  }

  /* ── SECTIONS ── */
  section { padding: 100px 48px; }

  .section-label {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 48px;
    display: flex;
    align-items: center;
    gap: 16px;
  }

  .section-label::after {
    content: '';
    flex: 1;
    max-width: 60px;
    height: 1px;
    background: var(--accent);
    opacity: 0.4;
  }

  /* ── STACK GRID ── */
  .stack-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    margin-bottom: 64px;
  }

  .stack-title {
    font-family: 'Bebas Neue', cursive;
    font-size: clamp(40px, 6vw, 72px);
    line-height: 1;
    letter-spacing: 0.02em;
  }

  .stack-count {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    color: rgba(245,242,238,0.3);
    letter-spacing: 0.1em;
  }

  .tech-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 1px;
    background: rgba(245,242,238,0.06);
    border: 1px solid rgba(245,242,238,0.06);
  }

  .tech-card {
    background: var(--ink);
    padding: 32px 28px;
    position: relative;
    cursor: default;
    transition: background 0.3s;
    overflow: hidden;
  }

  .tech-card::before {
    content: '';
    position: absolute;
    inset: 0;
    background: var(--accent);
    transform: translateY(100%);
    transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    z-index: 0;
  }

  .tech-card:hover::before { transform: translateY(0); }
  .tech-card:hover .tech-name { color: var(--ink); }
  .tech-card:hover .tech-role { color: rgba(10,10,10,0.5); }
  .tech-card:hover .tech-icon { color: var(--ink); }

  .tech-card > * { position: relative; z-index: 1; }

  .tech-icon {
    font-size: 22px;
    margin-bottom: 20px;
    color: rgba(245,242,238,0.3);
    font-family: 'DM Mono', monospace;
    transition: color 0.3s;
  }

  .tech-name {
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
    font-size: 16px;
    color: var(--paper);
    margin-bottom: 6px;
    transition: color 0.3s;
  }

  .tech-role {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: rgba(245,242,238,0.3);
    transition: color 0.3s;
  }

  /* ── FEATURES ── */
  .features-bg {
    background: #0f0f0f;
    margin: 0 -48px;
    padding: 100px 48px;
  }

  .features-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1px;
    background: rgba(245,242,238,0.06);
    border: 1px solid rgba(245,242,238,0.06);
    margin-top: 64px;
  }

  .feature-card {
    background: #0f0f0f;
    padding: 40px 36px;
    transition: background 0.3s;
  }

  .feature-card:hover { background: #141414; }

  .feature-number {
    font-family: 'Bebas Neue', cursive;
    font-size: 48px;
    line-height: 1;
    color: rgba(245,242,238,0.05);
    margin-bottom: 20px;
    letter-spacing: 0.05em;
  }

  .feature-title {
    font-size: 17px;
    font-weight: 500;
    color: var(--paper);
    margin-bottom: 12px;
  }

  .feature-desc {
    font-size: 14px;
    color: rgba(245,242,238,0.4);
    line-height: 1.7;
  }

  .feature-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 20px;
  }

  .tag {
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 5px 10px;
    border: 1px solid rgba(245,242,238,0.1);
    color: rgba(245,242,238,0.35);
  }

  /* ── ARCHITECTURE ── */
  .arch-section { padding: 100px 48px; }

  .arch-diagram {
    margin-top: 64px;
    position: relative;
  }

  .arch-layer {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-bottom: 12px;
    opacity: 0;
    transform: translateY(20px);
    transition: opacity 0.6s, transform 0.6s;
  }

  .arch-layer.visible { opacity: 1; transform: translateY(0); }

  .arch-layer-label {
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: rgba(245,242,238,0.2);
    margin-bottom: 8px;
  }

  .arch-module {
    background: rgba(245,242,238,0.04);
    border: 1px solid rgba(245,242,238,0.08);
    padding: 16px 18px;
    transition: background 0.3s, border-color 0.3s;
    cursor: default;
  }

  .arch-module:hover {
    background: rgba(200,255,0,0.06);
    border-color: rgba(200,255,0,0.25);
  }

  .arch-module-name {
    font-size: 13px;
    font-weight: 500;
    color: var(--paper);
    margin-bottom: 4px;
  }

  .arch-module-path {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    color: rgba(200,255,0,0.5);
  }

  .arch-arrow-row {
    display: flex;
    justify-content: center;
    padding: 4px 0;
    color: rgba(245,242,238,0.15);
    font-size: 18px;
  }

  /* ── AUTH FLOW ── */
  .auth-section {
    background: #060606;
    margin: 0 -48px;
    padding: 100px 48px;
  }

  .auth-flow {
    margin-top: 64px;
    display: flex;
    align-items: center;
    gap: 0;
    overflow-x: auto;
    padding-bottom: 20px;
  }

  .auth-step {
    flex-shrink: 0;
    width: 180px;
    background: rgba(245,242,238,0.03);
    border: 1px solid rgba(245,242,238,0.07);
    padding: 24px 20px;
    position: relative;
    transition: all 0.3s;
  }

  .auth-step:hover {
    background: rgba(245,242,238,0.06);
    border-color: rgba(200,255,0,0.3);
    transform: translateY(-4px);
  }

  .auth-step.active {
    background: rgba(200,255,0,0.07);
    border-color: rgba(200,255,0,0.4);
  }

  .auth-step-num {
    font-family: 'Bebas Neue', cursive;
    font-size: 36px;
    color: rgba(245,242,238,0.06);
    line-height: 1;
    margin-bottom: 12px;
  }

  .auth-step-name {
    font-size: 13px;
    font-weight: 500;
    color: var(--paper);
    margin-bottom: 6px;
  }

  .auth-step-desc {
    font-size: 11px;
    color: rgba(245,242,238,0.35);
    line-height: 1.6;
  }

  .auth-connector {
    flex-shrink: 0;
    display: flex;
    align-items: center;
    padding: 0 8px;
  }

  .auth-connector-line {
    width: 32px;
    height: 1px;
    background: rgba(245,242,238,0.1);
    position: relative;
  }

  .auth-connector-line::after {
    content: '▶';
    position: absolute;
    right: -6px;
    top: -6px;
    font-size: 10px;
    color: rgba(245,242,238,0.2);
  }

  /* ── STATS ROW ── */
  .stats-section {
    padding: 80px 48px;
    border-top: 1px solid rgba(245,242,238,0.05);
    border-bottom: 1px solid rgba(245,242,238,0.05);
  }

  .stats-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1px;
    background: rgba(245,242,238,0.06);
  }

  .stat-item {
    background: var(--ink);
    padding: 40px 32px;
    text-align: center;
  }

  .stat-num {
    font-family: 'Bebas Neue', cursive;
    font-size: 56px;
    line-height: 1;
    color: var(--accent);
    letter-spacing: 0.02em;
    margin-bottom: 8px;
  }

  .stat-label {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: rgba(245,242,238,0.3);
  }

  /* ── INSTALL ── */
  .install-section { padding: 100px 48px; }

  .install-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 48px;
    margin-top: 64px;
  }

  .install-steps {
    display: flex;
    flex-direction: column;
    gap: 24px;
  }

  .install-step {
    display: flex;
    gap: 20px;
    align-items: flex-start;
    opacity: 0;
    transform: translateX(-20px);
    transition: opacity 0.5s, transform 0.5s;
  }

  .install-step.visible { opacity: 1; transform: translateX(0); }

  .step-dot {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: rgba(200,255,0,0.1);
    border: 1px solid rgba(200,255,0,0.3);
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    color: var(--accent);
    flex-shrink: 0;
    margin-top: 4px;
  }

  .step-content-title {
    font-size: 14px;
    font-weight: 500;
    color: var(--paper);
    margin-bottom: 8px;
  }

  .code-block {
    background: rgba(245,242,238,0.04);
    border: 1px solid rgba(245,242,238,0.07);
    padding: 14px 18px;
    font-family: 'DM Mono', monospace;
    font-size: 12px;
    color: rgba(200,255,0,0.7);
    line-height: 1.8;
    white-space: pre;
    overflow-x: auto;
  }

  .code-block .dim { color: rgba(245,242,238,0.2); }
  .code-block .cmd { color: rgba(200,255,0,0.85); }
  .code-block .comment { color: rgba(245,242,238,0.18); }

  /* ── TERMINAL ── */
  .terminal {
    background: #000;
    border: 1px solid rgba(245,242,238,0.1);
    padding: 0;
    overflow: hidden;
  }

  .terminal-bar {
    background: rgba(245,242,238,0.05);
    padding: 10px 16px;
    display: flex;
    align-items: center;
    gap: 8px;
    border-bottom: 1px solid rgba(245,242,238,0.06);
  }

  .dot { width: 10px; height: 10px; border-radius: 50%; }
  .dot.r { background: #ff5f57; }
  .dot.y { background: #febc2e; }
  .dot.g { background: #28c840; }

  .terminal-title {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    color: rgba(245,242,238,0.2);
    margin-left: auto;
    letter-spacing: 0.08em;
  }

  .terminal-body {
    padding: 20px;
    font-family: 'DM Mono', monospace;
    font-size: 12px;
    line-height: 2;
    color: rgba(245,242,238,0.7);
  }

  .term-line { display: block; }
  .term-line.prompt { color: var(--accent); }
  .term-line.output { color: rgba(245,242,238,0.35); padding-left: 16px; }
  .term-line.success { color: #28c840; }
  .term-cursor {
    display: inline-block;
    width: 8px;
    height: 14px;
    background: var(--accent);
    animation: blink 1.2s step-end infinite;
    vertical-align: text-bottom;
  }

  @keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0; }
  }

  /* ── FOOTER ── */
  footer {
    padding: 80px 48px 48px;
    border-top: 1px solid rgba(245,242,238,0.06);
  }

  .footer-top {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 64px;
  }

  .footer-logo {
    font-family: 'Bebas Neue', cursive;
    font-size: 56px;
    letter-spacing: 0.05em;
    color: rgba(245,242,238,0.08);
    line-height: 1;
  }

  .footer-tagline {
    font-size: 13px;
    color: rgba(245,242,238,0.2);
    margin-top: 8px;
    font-style: italic;
  }

  .footer-badges {
    display: flex;
    flex-direction: column;
    gap: 10px;
    align-items: flex-end;
  }

  .badge {
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 6px 14px;
    border: 1px solid rgba(245,242,238,0.1);
    color: rgba(245,242,238,0.3);
  }

  .badge.live {
    border-color: rgba(200,255,0,0.3);
    color: var(--accent);
    background: rgba(200,255,0,0.04);
  }

  .footer-bottom {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 24px;
    border-top: 1px solid rgba(245,242,238,0.05);
  }

  .footer-copy {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    color: rgba(245,242,238,0.15);
    letter-spacing: 0.08em;
  }

  .footer-stack-pills {
    display: flex;
    gap: 8px;
  }

  .pill {
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    letter-spacing: 0.08em;
    padding: 4px 10px;
    border: 1px solid rgba(245,242,238,0.06);
    color: rgba(245,242,238,0.2);
  }

  /* ── ANIMATIONS ── */
  @keyframes fadeUp {
    to { opacity: 1; transform: translateY(0); }
  }

  .reveal {
    opacity: 0;
    transform: translateY(28px);
    transition: opacity 0.7s, transform 0.7s;
  }

  .reveal.visible {
    opacity: 1;
    transform: translateY(0);
  }

  /* ── FLOATING GRID BG ── */
  .hero-grid {
    position: absolute;
    inset: 0;
    background-image:
      linear-gradient(rgba(245,242,238,0.025) 1px, transparent 1px),
      linear-gradient(90deg, rgba(245,242,238,0.025) 1px, transparent 1px);
    background-size: 64px 64px;
    animation: gridDrift 40s linear infinite;
    pointer-events: none;
  }

  @keyframes gridDrift {
    from { transform: translate(0, 0); }
    to { transform: translate(64px, 64px); }
  }

  .hero-glow {
    position: absolute;
    width: 600px;
    height: 600px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(200,255,0,0.04) 0%, transparent 70%);
    right: -100px;
    top: 50%;
    transform: translateY(-50%);
    pointer-events: none;
    animation: glowPulse 6s ease-in-out infinite;
  }

  @keyframes glowPulse {
    0%, 100% { opacity: 0.6; transform: translateY(-50%) scale(1); }
    50% { opacity: 1; transform: translateY(-50%) scale(1.05); }
  }

  @media (max-width: 768px) {
    nav { padding: 16px 24px; }
    section { padding: 64px 24px; }
    .hero { padding: 100px 24px 64px; }
    .features-grid { grid-template-columns: 1fr; }
    .install-grid { grid-template-columns: 1fr; }
    .stats-grid { grid-template-columns: repeat(2, 1fr); }
    .arch-layer { grid-template-columns: repeat(2, 1fr); }
    .footer-top { flex-direction: column; gap: 32px; }
    .footer-badges { align-items: flex-start; }
    .footer-bottom { flex-direction: column; gap: 16px; align-items: flex-start; }
  }
</style>
</head>
<body>

<div id="progress"></div>

<!-- NAV -->
<nav>
  <a class="nav-logo" href="#">NØ & CO.</a>
  <span class="nav-badge">Django · PostgreSQL · v1.0</span>
</nav>

<!-- HERO -->
<section class="hero">
  <div class="hero-grid"></div>
  <div class="hero-glow"></div>
  <p class="hero-eyebrow">Fashion E-Commerce Platform</p>
  <h1 class="hero-title">NØ &amp;<br><span class="stroke">CO.</span></h1>
  <p class="hero-sub">A premium fashion e-commerce destination built for the modern consumer. Scandinavian minimalist aesthetic, engineered for scalability and excellence.</p>
  <div class="hero-cta-row">
    <a href="#stack" class="btn-primary">
      Explore Stack
      <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
        <path d="M2 7h10M8 3l4 4-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </a>
    <a href="#architecture" class="btn-ghost">View Architecture</a>
  </div>
</section>

<!-- MARQUEE -->
<div class="marquee-section">
  <div class="marquee-track" id="marquee">
    <span class="marquee-item">Python 3.x</span>
    <span class="marquee-item accent">·</span>
    <span class="marquee-item">Django 4.x</span>
    <span class="marquee-item accent">·</span>
    <span class="marquee-item">PostgreSQL</span>
    <span class="marquee-item accent">·</span>
    <span class="marquee-item">Tailwind CSS</span>
    <span class="marquee-item accent">·</span>
    <span class="marquee-item">JavaScript</span>
    <span class="marquee-item accent">·</span>
    <span class="marquee-item">Razorpay</span>
    <span class="marquee-item accent">·</span>
    <span class="marquee-item">JWT Auth</span>
    <span class="marquee-item accent">·</span>
    <span class="marquee-item">MVC Architecture</span>
    <span class="marquee-item accent">·</span>
    <!-- duplicate for seamless loop -->
    <span class="marquee-item">Python 3.x</span>
    <span class="marquee-item accent">·</span>
    <span class="marquee-item">Django 4.x</span>
    <span class="marquee-item accent">·</span>
    <span class="marquee-item">PostgreSQL</span>
    <span class="marquee-item accent">·</span>
    <span class="marquee-item">Tailwind CSS</span>
    <span class="marquee-item accent">·</span>
    <span class="marquee-item">JavaScript</span>
    <span class="marquee-item accent">·</span>
    <span class="marquee-item">Razorpay</span>
    <span class="marquee-item accent">·</span>
    <span class="marquee-item">JWT Auth</span>
    <span class="marquee-item accent">·</span>
    <span class="marquee-item">MVC Architecture</span>
    <span class="marquee-item accent">·</span>
  </div>
</div>

<!-- STATS -->
<div class="stats-section reveal" id="stats">
  <div class="stats-grid">
    <div class="stat-item">
      <div class="stat-num" data-target="8">0</div>
      <div class="stat-label">Django Apps</div>
    </div>
    <div class="stat-item">
      <div class="stat-num" data-target="7">0</div>
      <div class="stat-label">Tech Stack Layers</div>
    </div>
    <div class="stat-item">
      <div class="stat-num" data-target="3">0</div>
      <div class="stat-label">Payment Methods</div>
    </div>
    <div class="stat-item">
      <div class="stat-num" data-target="100">0</div>
      <div class="stat-label">% Production Ready</div>
    </div>
  </div>
</div>

<!-- TECH STACK -->
<section id="stack">
  <div class="section-label">Full Stack</div>
  <div class="stack-header">
    <h2 class="stack-title reveal">The<br>Tech Stack</h2>
    <span class="stack-count reveal">07 Technologies</span>
  </div>
  <div class="tech-grid reveal">
    <div class="tech-card">
      <div class="tech-icon">🐍</div>
      <div class="tech-name">Python 3.x</div>
      <div class="tech-role">Core Language</div>
    </div>
    <div class="tech-card">
      <div class="tech-icon">⬡</div>
      <div class="tech-name">Django 4.x</div>
      <div class="tech-role">Web Framework · MVC</div>
    </div>
    <div class="tech-card">
      <div class="tech-icon">🐘</div>
      <div class="tech-name">PostgreSQL</div>
      <div class="tech-role">Primary Database</div>
    </div>
    <div class="tech-card">
      <div class="tech-icon">◈</div>
      <div class="tech-name">Tailwind CSS</div>
      <div class="tech-role">Utility Styling</div>
    </div>
    <div class="tech-card">
      <div class="tech-icon">JS</div>
      <div class="tech-name">JavaScript</div>
      <div class="tech-role">Frontend Logic</div>
    </div>
    <div class="tech-card">
      <div class="tech-icon">&lt;/&gt;</div>
      <div class="tech-name">HTML5 · CSS3</div>
      <div class="tech-role">Structure · Design</div>
    </div>
    <div class="tech-card">
      <div class="tech-icon">⟁</div>
      <div class="tech-name">Git</div>
      <div class="tech-role">Version Control</div>
    </div>
  </div>
</section>

<!-- FEATURES -->
<div class="features-bg">
  <section style="padding:0;">
    <div class="section-label reveal">Platform Features</div>
    <h2 class="stack-title reveal">Built for<br>Everything</h2>
    <div class="features-grid">
      <div class="feature-card reveal">
        <div class="feature-number">01</div>
        <div class="feature-title">Advanced Product Catalog</div>
        <div class="feature-desc">Multi-variant support with Color & Size combinations and real-time inventory tracking at the variant level.</div>
        <div class="feature-tags">
          <span class="tag">Variants</span>
          <span class="tag">Stock Alerts</span>
          <span class="tag">Image Cropper</span>
        </div>
      </div>
      <div class="feature-card reveal">
        <div class="feature-number">02</div>
        <div class="feature-title">Secure Authentication</div>
        <div class="feature-desc">JWT/Session-based auth with password recovery, Google OAuth, and secure session management throughout.</div>
        <div class="feature-tags">
          <span class="tag">JWT</span>
          <span class="tag">Sessions</span>
          <span class="tag">Recovery</span>
        </div>
      </div>
      <div class="feature-card reveal">
        <div class="feature-number">03</div>
        <div class="feature-title">Smart Checkout Flow</div>
        <div class="feature-desc">Streamlined multi-step checkout with Razorpay integration, wallet payments, and coupon validation engine.</div>
        <div class="feature-tags">
          <span class="tag">Razorpay</span>
          <span class="tag">Wallet</span>
          <span class="tag">Coupons</span>
        </div>
      </div>
      <div class="feature-card reveal">
        <div class="feature-number">04</div>
        <div class="feature-title">Offer Engine</div>
        <div class="feature-desc">Category-wise and product-wise dynamic pricing with countdown timers and automated discount application.</div>
        <div class="feature-tags">
          <span class="tag">Countdown</span>
          <span class="tag">Category Offers</span>
          <span class="tag">Auto-Apply</span>
        </div>
      </div>
      <div class="feature-card reveal">
        <div class="feature-number">05</div>
        <div class="feature-title">Order Management</div>
        <div class="feature-desc">Full order lifecycle: history, real-time status tracking, cancellations, returns, and instant wallet refunds.</div>
        <div class="feature-tags">
          <span class="tag">Returns</span>
          <span class="tag">Tracking</span>
          <span class="tag">Refunds</span>
        </div>
      </div>
      <div class="feature-card reveal">
        <div class="feature-number">06</div>
        <div class="feature-title">Admin Dashboard</div>
        <div class="feature-desc">Bespoke management interface for products, orders, users, stock control and platform-wide discount management.</div>
        <div class="feature-tags">
          <span class="tag">Analytics</span>
          <span class="tag">User Mgmt</span>
          <span class="tag">Stock Control</span>
        </div>
      </div>
    </div>
  </section>
</div>

<!-- ARCHITECTURE -->
<section class="arch-section" id="architecture">
  <div class="section-label reveal">Project Structure</div>
  <h2 class="stack-title reveal">MVC<br>Architecture</h2>

  <div class="arch-diagram">
    <div class="arch-layer-label" style="margin-top:32px;">Frontend Layer</div>
    <div class="arch-layer" id="layer-1">
      <div class="arch-module"><div class="arch-module-name">Templates</div><div class="arch-module-path">/templates/</div></div>
      <div class="arch-module"><div class="arch-module-name">Static Assets</div><div class="arch-module-path">/static/</div></div>
      <div class="arch-module"><div class="arch-module-name">Tailwind CSS</div><div class="arch-module-path">styling layer</div></div>
      <div class="arch-module"><div class="arch-module-name">JavaScript</div><div class="arch-module-path">client logic</div></div>
    </div>

    <div class="arch-arrow-row">↓</div>

    <div class="arch-layer-label">Application Layer</div>
    <div class="arch-layer" id="layer-2">
      <div class="arch-module"><div class="arch-module-name">Accounts</div><div class="arch-module-path">/accounts/</div></div>
      <div class="arch-module"><div class="arch-module-name">Products</div><div class="arch-module-path">/products/</div></div>
      <div class="arch-module"><div class="arch-module-name">Cart</div><div class="arch-module-path">/cart/</div></div>
      <div class="arch-module"><div class="arch-module-name">Orders</div><div class="arch-module-path">/order_management/</div></div>
    </div>

    <div class="arch-arrow-row">↓</div>

    <div class="arch-layer-label">Business Logic</div>
    <div class="arch-layer" id="layer-3">
      <div class="arch-module"><div class="arch-module-name">Wallet</div><div class="arch-module-path">/wallet/</div></div>
      <div class="arch-module"><div class="arch-module-name">Coupons</div><div class="arch-module-path">/coupon/</div></div>
      <div class="arch-module"><div class="arch-module-name">Category</div><div class="arch-module-path">/category/</div></div>
      <div class="arch-module"><div class="arch-module-name">Core</div><div class="arch-module-path">/core/</div></div>
    </div>

    <div class="arch-arrow-row">↓</div>

    <div class="arch-layer-label">Data Layer</div>
    <div class="arch-layer" id="layer-4" style="grid-template-columns:repeat(2,1fr); max-width:460px;">
      <div class="arch-module"><div class="arch-module-name">Django ORM</div><div class="arch-module-path">models.py</div></div>
      <div class="arch-module"><div class="arch-module-name">PostgreSQL</div><div class="arch-module-path">primary database</div></div>
    </div>
  </div>
</section>

<!-- AUTH FLOW -->
<div class="auth-section">
  <section style="padding:0;">
    <div class="section-label reveal">Security</div>
    <h2 class="stack-title reveal">Auth Flow</h2>
    <div class="auth-flow reveal" style="margin-top:48px;">
      <div class="auth-step">
        <div class="auth-step-num">01</div>
        <div class="auth-step-name">Request</div>
        <div class="auth-step-desc">User submits credentials via secure form</div>
      </div>
      <div class="auth-connector"><div class="auth-connector-line"></div></div>
      <div class="auth-step active">
        <div class="auth-step-num">02</div>
        <div class="auth-step-name">Validate</div>
        <div class="auth-step-desc">Django auth validates against PostgreSQL</div>
      </div>
      <div class="auth-connector"><div class="auth-connector-line"></div></div>
      <div class="auth-step">
        <div class="auth-step-num">03</div>
        <div class="auth-step-name">JWT Issue</div>
        <div class="auth-step-desc">Token generated and session created</div>
      </div>
      <div class="auth-connector"><div class="auth-connector-line"></div></div>
      <div class="auth-step">
        <div class="auth-step-num">04</div>
        <div class="auth-step-name">Middleware</div>
        <div class="auth-step-desc">Every request passes through auth middleware</div>
      </div>
      <div class="auth-connector"><div class="auth-connector-line"></div></div>
      <div class="auth-step">
        <div class="auth-step-num">05</div>
        <div class="auth-step-name">Access</div>
        <div class="auth-step-desc">Protected views and API endpoints unlocked</div>
      </div>
    </div>
  </section>
</div>

<!-- INSTALL -->
<section class="install-section" id="install">
  <div class="section-label reveal">Getting Started</div>
  <h2 class="stack-title reveal">Setup in<br>5 Steps</h2>

  <div class="install-grid">
    <div class="install-steps">
      <div class="install-step" id="s1">
        <div class="step-dot">01</div>
        <div>
          <div class="step-content-title">Clone Repository</div>
          <div class="code-block"><span class="cmd">git clone</span> github.com/yourusername/no-and-co
<span class="dim">cd</span> no-and-co</div>
        </div>
      </div>
      <div class="install-step" id="s2">
        <div class="step-dot">02</div>
        <div>
          <div class="step-content-title">Virtual Environment</div>
          <div class="code-block"><span class="dim">python -m venv</span> venv
<span class="cmd">source</span> venv/bin/activate</div>
        </div>
      </div>
      <div class="install-step" id="s3">
        <div class="step-dot">03</div>
        <div>
          <div class="step-content-title">Install Dependencies</div>
          <div class="code-block"><span class="dim">pip install</span> <span class="cmd">-r requirements.txt</span></div>
        </div>
      </div>
      <div class="install-step" id="s4">
        <div class="step-dot">04</div>
        <div>
          <div class="step-content-title">Database Migrations</div>
          <div class="code-block"><span class="dim">python manage.py</span> <span class="cmd">makemigrations</span>
<span class="dim">python manage.py</span> <span class="cmd">migrate</span></div>
        </div>
      </div>
      <div class="install-step" id="s5">
        <div class="step-dot">05</div>
        <div>
          <div class="step-content-title">Run Server</div>
          <div class="code-block"><span class="dim">python manage.py</span> <span class="cmd">runserver</span></div>
        </div>
      </div>
    </div>

    <div class="terminal">
      <div class="terminal-bar">
        <div class="dot r"></div>
        <div class="dot y"></div>
        <div class="dot g"></div>
        <span class="terminal-title">bash — no_and_co</span>
      </div>
      <div class="terminal-body" id="terminal-body">
        <span class="term-line prompt">$ git clone github.com/yourusername/no-and-co</span>
        <span class="term-line output">Cloning into 'no-and-co'...</span>
        <span class="term-line output">remote: Counting objects: 312, done.</span>
        <span class="term-line output">Receiving objects: 100% (312/312), done.</span>
        <span class="term-line prompt">$ cd no-and-co && source venv/bin/activate</span>
        <span class="term-line success">(venv) ✓ Environment activated</span>
        <span class="term-line prompt">$ pip install -r requirements.txt</span>
        <span class="term-line output">Collecting Django==4.2.7</span>
        <span class="term-line output">Collecting psycopg2-binary</span>
        <span class="term-line output">Collecting razorpay</span>
        <span class="term-line success">Successfully installed 24 packages</span>
        <span class="term-line prompt">$ python manage.py migrate</span>
        <span class="term-line output">Running migrations for accounts...</span>
        <span class="term-line output">Running migrations for products...</span>
        <span class="term-line success">✓ All migrations applied</span>
        <span class="term-line prompt">$ python manage.py runserver</span>
        <span class="term-line success">Django v4.2.7 · Starting server at 127.0.0.1:8000</span>
        <span class="term-line prompt">$ <span class="term-cursor"></span></span>
      </div>
    </div>
  </div>
</section>

<!-- FOOTER -->
<footer>
  <div class="footer-top">
    <div>
      <div class="footer-logo">NØ & CO.</div>
      <div class="footer-tagline">Redefining Digital Fashion.</div>
    </div>
    <div class="footer-badges">
      <div class="badge live">● Production Ready</div>
      <div class="badge">MVC Architecture</div>
      <div class="badge">Django 4.x</div>
      <div class="badge">PostgreSQL</div>
    </div>
  </div>
  <div class="footer-bottom">
    <span class="footer-copy">Developed with ❤ for the Modern Fashion Industry</span>
    <div class="footer-stack-pills">
      <span class="pill">Python</span>
      <span class="pill">Django</span>
      <span class="pill">PostgreSQL</span>
      <span class="pill">Tailwind</span>
    </div>
  </div>
</footer>

<script>
  // Progress bar
  window.addEventListener('scroll', () => {
    const p = (window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100;
    document.getElementById('progress').style.width = p + '%';
  });

  // Intersection observer for reveals
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add('visible');
      }
    });
  }, { threshold: 0.12 });

  document.querySelectorAll('.reveal').forEach(el => observer.observe(el));

  // Architecture layers stagger
  const layers = document.querySelectorAll('.arch-layer');
  const layerObs = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        const idx = [...layers].indexOf(e.target);
        setTimeout(() => e.target.classList.add('visible'), idx * 150);
      }
    });
  }, { threshold: 0.1 });
  layers.forEach(l => layerObs.observe(l));

  // Install steps stagger
  const steps = ['s1','s2','s3','s4','s5'];
  const stepObs = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        steps.forEach((id, i) => {
          setTimeout(() => {
            const el = document.getElementById(id);
            if (el) el.classList.add('visible');
          }, i * 120);
        });
        stepObs.disconnect();
      }
    });
  }, { threshold: 0.1 });
  const firstStep = document.getElementById('s1');
  if (firstStep) stepObs.observe(firstStep);

  // Counter animation
  function animateCounter(el, target, duration) {
    let start = 0;
    const step = (timestamp) => {
      if (!start) start = timestamp;
      const progress = Math.min((timestamp - start) / duration, 1);
      const ease = 1 - Math.pow(1 - progress, 3);
      el.textContent = Math.round(ease * target);
      if (progress < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }

  const statsObs = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        document.querySelectorAll('[data-target]').forEach(el => {
          animateCounter(el, parseInt(el.dataset.target), 1400);
        });
        statsObs.disconnect();
      }
    });
  }, { threshold: 0.3 });
  const statsEl = document.getElementById('stats');
  if (statsEl) statsObs.observe(statsEl);
</script>

</body>
</html>
