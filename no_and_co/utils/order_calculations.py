from decimal import Decimal, ROUND_HALF_UP

class OrderCalculator:
    """
    Centralized utility for ecommerce money calculations.
    Follows Amazon/Myntra style proportional distribution.
    Ensures mathematical integrity and prevents rounding leaks.
    """

    @staticmethod
    def round_money(amount):
        if amount is None:
            return Decimal('0.00')
        return Decimal(amount).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    @classmethod
    def distribute_proportionally(cls, items_data, total_to_distribute, base_total):
        """
        Generic proportional distribution logic.
        """
        if not total_to_distribute or total_to_distribute <= 0 or not base_total or base_total <= 0:
            return {item['id']: Decimal('0.00') for item in items_data}

        distributions = {}
        remaining = cls.round_money(total_to_distribute)

        for i, item in enumerate(items_data):
            if i == len(items_data) - 1:
                distributions[item['id']] = remaining
            else:
                line_total = cls.round_money(item['price'] * item['quantity'])
                share = cls.round_money((line_total / base_total) * total_to_distribute)
                
                # Prevent over-distribution
                if share > remaining:
                    share = remaining
                
                distributions[item['id']] = share
                remaining -= share
        
        return distributions

    @classmethod
    def calculate_order_shares(cls, items_data, total_coupon_discount, total_tax_amount):
        """
        Distributes coupon and tax across items.
        """
        subtotal = sum(cls.round_money(item['price'] * item['quantity']) for item in items_data)
        
        coupon_shares = cls.distribute_proportionally(items_data, total_coupon_discount, subtotal)
        tax_shares = cls.distribute_proportionally(items_data, total_tax_amount, subtotal)
        
        results = {}
        for item in items_data:
            id = item['id']
            c_share = coupon_shares[id]
            t_share = tax_shares[id]
            line_base = cls.round_money(item['price'] * item['quantity'])
            
            results[id] = {
                'coupon_share': c_share,
                'tax_share': t_share,
                'net_paid': cls.round_money(line_base - c_share + t_share)
            }
            
        return results
