
from decimal import Decimal
from django.utils import timezone
from .models import Offer, OfferProduct, OfferCategory

def get_best_offer(product, price):
    """
    Finds the best instant discount offer for a given product and price.
    Only considers offers with min_purchase=0 (instant discounts).
    Returns (best_offer, discount_amount)
    """
    today = timezone.now().date()
    
    # 1. Get all valid active instant offers for the product
    product_offers = Offer.objects.filter(
        apply_to='product',
        is_active=True,
        min_purchase=0,
        start_date__lte=today,
        end_date__gte=today,
        offerproduct__product=product
    )
    
    # 2. Get all valid active instant offers for the product's category
    category_offers = Offer.objects.filter(
        apply_to='category',
        is_active=True,
        min_purchase=0,
        start_date__lte=today,
        end_date__gte=today,
        offercategory__category=product.category
    )
    
    best_offer = None
    max_discount_amount = Decimal('0.00')
    
    all_offers = list(product_offers) + list(category_offers)
    
    for offer in all_offers:
        current_discount = Decimal('0.00')
        if offer.discount_type == 'percentage':
            current_discount = price * (offer.discount_value / Decimal('100'))
            if offer.max_discount and current_discount > offer.max_discount:
                current_discount = offer.max_discount
        else: # flat
            current_discount = offer.discount_value
        
        if current_discount > max_discount_amount:
            max_discount_amount = current_discount
            best_offer = offer
            
    return best_offer, max_discount_amount.quantize(Decimal('0.01'))

def apply_offers_to_variants(variants):
    """
    Attaches final_price, original_price, and discount_percent to each variant.
    Uses prefetching to be efficient.
    """
    if not variants:
        return variants
        
    today = timezone.now().date()
    
    # Get all active instant offers
    # We pre-fetch these to avoid N+1 inside the loop
    all_active_offers = Offer.objects.filter(
        is_active=True,
        min_purchase=0,
        start_date__lte=today,
        end_date__gte=today
    ).prefetch_related('offerproduct_set', 'offercategory_set')
    
    # Map offers to products and categories for fast lookup
    product_offer_map = {} # product_id -> [offers]
    category_offer_map = {} # category_id -> [offers]
    
    for offer in all_active_offers:
        if offer.apply_to == 'product':
            for op in offer.offerproduct_set.all():
                if op.product_id not in product_offer_map:
                    product_offer_map[op.product_id] = []
                product_offer_map[op.product_id].append(offer)
        else:
            for oc in offer.offercategory_set.all():
                if oc.category_id not in category_offer_map:
                    category_offer_map[oc.category_id] = []
                category_offer_map[oc.category_id].append(offer)
    
    for variant in variants:
        product = variant.product
        price = variant.price
        
        applicable_offers = product_offer_map.get(product.id, []) + category_offer_map.get(product.category.id, [])
        
        best_discount = Decimal('0.00')
        final_price = price
        discount_percent = 0
        
        for offer in applicable_offers:
            current_discount = Decimal('0.00')
            if offer.discount_type == 'percentage':
                current_discount = price * (offer.discount_value / Decimal('100'))
                if offer.max_discount and current_discount > offer.max_discount:
                    current_discount = offer.max_discount
            else: # flat
                current_discount = offer.discount_value
            
            if current_discount > best_discount:
                best_discount = current_discount
        
        if best_discount > 0:
            final_price = price - best_discount
            if final_price < 0: final_price = Decimal('0.00')
            
            # Calculate actual percentage for display
            discount_percent = int((best_discount / price) * 100)
            if discount_percent > 100: discount_percent = 100
            
        variant.original_price = price
        variant.final_price = final_price.quantize(Decimal('0.01'))
        variant.discount_percent = discount_percent
        variant.has_discount = best_discount > 0
        variant.savings = (price - final_price).quantize(Decimal('0.01'))
        
    return variants
