from decimal import Decimal
from django.utils import timezone
from .models import Offer, OfferProduct, OfferCategory


def calculate_discount_amount(offer, price):
    """Helper to calculate individual offer discount amount"""
    discount = Decimal('0.00')
    if offer.discount_type == 'percentage':
        discount = price * (offer.discount_value / Decimal('100'))
        if offer.max_discount and discount > offer.max_discount:
            discount = offer.max_discount
    else: # flat
        discount = offer.discount_value
    return discount.quantize(Decimal('0.01'))

def calculate_final_price(product, price):
    """
    Core pricing engine enforcing: Product Offer > Category Offer > Original Price.
    Returns (final_price, original_price, discount_percent, has_active_offer, savings)
    """
    today = timezone.now().date()
    best_discount = Decimal('0.00')
    winning_offer = None
    
    # Priority 1: Product Offers
    product_offers = Offer.objects.filter(
        apply_to='product',
        is_active=True,
        start_date__lte=today,
        end_date__gte=today,
        offerproduct__product=product
    )
    
    found_pd = False
    for o in product_offers:
        if o.min_purchase <= price:
            disc = calculate_discount_amount(o, price)
            if disc > best_discount:
                best_discount = disc
                winning_offer = o
                found_pd = True
    
    if not found_pd:
        # Priority 2: Category Offers
        category_offers = Offer.objects.filter(
            apply_to='category',
            is_active=True,
            start_date__lte=today,
            end_date__gte=today,
            offercategory__category=product.category
        )
        for o in category_offers:
            if o.min_purchase <= price:
                disc = calculate_discount_amount(o, price)
                if disc > best_discount:
                    best_discount = disc
                    winning_offer = o

    final_price = (price - best_discount).quantize(Decimal('0.01'))
    if final_price < 0: final_price = Decimal('0.00')
    
    discount_percent = 0
    if winning_offer:
        if winning_offer.discount_type == 'percentage':
            # Use EXACT stored value to avoid 19.98% floating point issues
            discount_percent = int(winning_offer.discount_value)
        else:
            # For flat discounts, we still calculate BUT round to zero/clean
            if price > 0:
                discount_percent = int((best_discount / price) * 100)
    
    return (
        final_price,
        price,
        discount_percent,
        best_discount > 0,
        best_discount
    )

def get_best_offer(product, price):
    """Legacy compatibility wrapper for cart/other views"""
    _, _, _, has_offer, amount = calculate_final_price(product, price)
    # Finding "best offer" object is expensive here, so returning None if not needed
    # but we mostly care about the discount amount in the project.
    return None, amount

def apply_offers_to_variants(variants):
    """
    Batch-optimized pricing engine.
    Fetches all active offers once and applies priority logic locally to avoid N+1.
    """
    if not variants:
        return variants
        
    today = timezone.now().date()
    # Fetch all potentially relevant active instant offers
    all_active_offers = Offer.objects.filter(
        is_active=True,
        start_date__lte=today,
        end_date__gte=today
    ).prefetch_related('offerproduct_set', 'offercategory_set')
    
    # Group by level for priority logic
    product_offer_map = {} 
    category_offer_map = {} 
    
    for offer in all_active_offers:
        if offer.apply_to == 'product':
            for op in offer.offerproduct_set.all():
                product_offer_map.setdefault(op.product_id, []).append(offer)
        else:
            for oc in offer.offercategory_set.all():
                category_offer_map.setdefault(oc.category_id, []).append(offer)
    
    for variant in variants:
        product = variant.product
        original_price = variant.price
        best_discount = Decimal('0.00')
        
        # Priority 1: Product Offers
        pd_offers = product_offer_map.get(product.id, [])
        winning_offer = None
        
        for o in pd_offers:
            if o.min_purchase <= original_price:
                disc = calculate_discount_amount(o, original_price)
                if disc > best_discount:
                    best_discount = disc
                    winning_offer = o
        
        if not winning_offer:
            # Priority 2: Category Offers
            category_id = getattr(product, 'category_id', None)
            cat_offers = category_offer_map.get(category_id, []) if category_id else []
            for o in cat_offers:
                if o.min_purchase <= original_price:
                    disc = calculate_discount_amount(o, original_price)
                    if disc > best_discount:
                        best_discount = disc
                        winning_offer = o
        
        final_price = (original_price - best_discount).quantize(Decimal('0.01'))
        if final_price < 0: final_price = Decimal('0.00')
        
        discount_percent = 0
        if winning_offer:
            if winning_offer.discount_type == 'percentage':
                # FIX: Use original stored percentage value directly
                discount_percent = int(winning_offer.discount_value)
            else:
                # Fallback for flat discounts
                if original_price > 0:
                    discount_percent = int((best_discount / original_price) * 100)
            
        variant.original_price = original_price
        variant.final_price = final_price
        variant.discount_percent = discount_percent
        variant.has_discount = best_discount > 0
        variant.savings = best_discount
        
    return variants
