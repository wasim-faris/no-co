import sys
import re

def update_cart():
    with open(r'cart/templates/cart.html', 'r', encoding='utf-8') as f:
        text = f.read()

    text = text.replace('.cart-title', '.page-heading')
    text = text.replace('<h1 class="cart-title">', '<h1 class="page-heading">')
    text = text.replace('font-size: clamp(2rem, 5vw, 4rem);', 'font-family: "Inter", "Helvetica Neue", Arial, sans-serif !important;\n        font-size: 36px;\n        line-height: 1.2;')
    text = text.replace('font-weight: 900;', 'font-weight: 500;')
    text = text.replace('letter-spacing: -0.04em;', 'letter-spacing: 0.06em;')
    text = re.sub(r'transform: scaleX\(1\.15\);\s*transform-origin: left;', '', text)

    if '@media (max-width: 600px)' not in text:
        text = text.replace('</style>', '    @media (max-width: 600px) {\n        .page-heading {\n            font-size: 24px;\n        }\n    }\n</style>')

    with open(r'cart/templates/cart.html', 'w', encoding='utf-8') as f:
        f.write(text)

def update_checkout():
    with open(r'core/templates/checkout.html', 'r', encoding='utf-8') as f:
        text = f.read()

    text = text.replace('.checkout-title', '.page-heading')
    text = text.replace('<h1 class="checkout-title">', '<h1 class="page-heading">')
    text = text.replace('font-size: 32px;', 'font-family: "Inter", "Helvetica Neue", Arial, sans-serif !important;\n        font-size: 36px;\n        line-height: 1.2;')
    text = text.replace('font-weight: 800;', 'font-weight: 500;')
    text = text.replace('letter-spacing: -0.02em;', 'letter-spacing: 0.06em;')

    if '@media (max-width: 600px)' not in text:
        text = text.replace('</style>', '    @media (max-width: 600px) {\n        .page-heading {\n            font-size: 24px;\n        }\n    }\n</style>')

    with open(r'core/templates/checkout.html', 'w', encoding='utf-8') as f:
        f.write(text)

update_cart()
update_checkout()
