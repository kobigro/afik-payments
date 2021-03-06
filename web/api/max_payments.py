from utils import get_class_id

# List of dynamic methods for max payments


def megamot_max_price(school, class_id):
    is_charging_for_additional_religious_program = school.payments.filter_by(
        clause='תוכנית לימודים נוספת תורנית', of_class=class_id).scalar() is not None
    # As anywhere, 0 means can't charge while None means there is no charging
    # limit. in this case, megamot is in voluntary payments, so it has no
    # payment limit
    return 0.0 if is_charging_for_additional_religious_program else None

MESIBAT_SIUM_MAX_PRICES = {
    'חט"ב + עליונה': 200.0,
    'יסודי ועליונה': 200.0,
    'יסודי חט"ב ועליונה': 200.0,
    'עליונה בלבד': 200.0,
    'חט"ב בלבד': 125.0,
    'יסודי וחט"ב': 125.0,
    'יסודי בלבד': 75.0
}


def mesibat_sium_max_price(school, class_id):
    # If the class is the final class of this school, for example 12th grade
    # in high school, it and only it can charge for a "mesibat sium"
    # according to hozer mankal
    if school.level == 'יסודי בלבד' and class_id == get_class_id('ח'):
        # A hack for elementary schools with an eighth grade. more details at
        # models.py TODO: fix without a hack.
        return MESIBAT_SIUM_MAX_PRICES['יסודי וחט"ב']

    charge_amount = MESIBAT_SIUM_MAX_PRICES.get(school.level)
    return charge_amount if charge_amount is not None else 0.0

"""
    The data structure describing all max prices, for
    payment types and payment clauses, dynamic and static clauses,etc.
    TODO: actually document this dict and the format according to which
    the school max prices are calculated(static, same_price_for_all,
    class_ranges_max_prices) etc. or, refactor into classes, 
    since this solution is ugly.
"""

PAYMENTS_MAX_PRICES = {
    'חובה': {
        'clauses':
        [
            {
                'name': 'ביטוח תאונות אישיות',
                'static': True,
                'same_price_for_all': True,
                'max_price': 75.0
            }
        ],
        'has_max_price': False
    },
    'רשות': {
        'clauses':
        [
            {
                'name': 'סל תרבות',
                'only_religious_schools': False,
                'static': True,
                'same_price_for_all': False,
                'class_ranges_max_prices': {
                    ('א', 'ח'): 99.0,
                    ('ט',): 165.0,
                    ('י', 'יב'): 176.0
                }
            },
            {
                'name': 'מסיבת סיום',
                'only_religious_schools': False,
                'static': False,
                'same_price_for_all': False,
                'max_price_func': mesibat_sium_max_price
            },
            {
                'name': 'מסיבות כיתתיות',
                'only_religious_schools': False,
                'static': True,
                'same_price_for_all': True,
                'max_price': 24.0
            },
            {
                'name': 'השאלת ספרי לימוד',
                'only_religious_schools': False,
                'static': True,
                'same_price_for_all': False,
                'class_ranges_max_prices': {
                    ('א', 'ט'): 280.0,
                    ('י', 'יב'): 320.0
                }
            },
            {
                'name': 'ארגון הורים ארצי',
                'only_religious_schools': False,
                'static': True,
                'same_price_for_all': True,
                'max_price': 1.5
            },
            {
                'name': 'ועד הורים ישובי',
                'only_religious_schools': False,
                'static': True,
                'same_price_for_all': True,
                'max_price': 1.5
            },
            {
                'name': 'עלות טיול לתלמיד באוטובוס של 40 תלמידים',
                'only_religious_schools': False,
                'static': True,
                'same_price_for_all': False,
                'class_ranges_max_prices': {
                    ('א', 'ב'): 101.0,
                    ('ג', 'ד'): 126.0,
                    ('ה',): 252.0,
                    ('ו', 'ט'): 387.0,
                    ('י', 'יא'): 513.0,
                    ('יב',): 616.0
                }
            },
            {
                'name': 'של"ח',
                'only_religious_schools': False,
                'static': True,
                'same_price_for_all': False,
                'class_ranges_max_prices': {
                    ('א', 'ו'): 0.0,
                    ('ז', 'יא'): 150.0,
                    ('יב',): 0.0
                }
            },
            {
                'name': 'הפעלת המוסד בשעות אחר הצהריים',
                'only_religious_schools': True,
                'static': True,
                'same_price_for_all': False,
                'class_ranges_max_prices': {
                    ('ה', 'ו'): 400.0,
                    ('ז', 'יב'): 600.0
                }
            }
        ],
        'has_max_price': False
    },
    'פעילות חברתית תורנית(סמינריונים ושבתות)': {
        'clauses':
        [
            {
                'name': 'סמינריון',
                'only_religious_schools': True,
                'static': True,
                'same_price_for_all': False,
                'class_ranges_max_prices': {
                    ('ז', 'יב'): 800.0
                },
                'price_for_one': {
                    ('ז', 'יב'): 400.0
                }
            },
            {
                'name': 'שבתות',
                'only_religious_schools': True,
                'static': True,
                'same_price_for_all': False,
                'class_ranges_max_prices': {
                    ('ז', 'יב'): 680.0
                },
                'price_for_one': {
                    ('ז', 'יב'): 340.0
                }
            }
        ],
        'has_max_price': False
    },
    'תוכנית לימודים נוספת': {
        'clauses': [
            {
                'name': 'תכנית לימודים נוספת',
                'only_religious_schools': False,
                'static': True,
                'same_price_for_all': False,
                'class_ranges_max_prices': {
                    ('א', 'ו'): 885.0,
                    ('ז', 'ט'): 1060.0,
                    ('י', 'יב'): 1150.0
                },
                # repesents price for a single 'item',
                # in talan, price for one hour
                # in shabbat & seminarion,
                # price for one shabbat / seminarion, etc.

                'price_for_one': {
                    ('א', 'ו'): 177.0,
                    ('ז', 'ט'): 212.0,
                    ('י', 'יב'): 230.0
                }
            },
            {
                'name': 'תוכנית לימודים נוספת תורנית',
                'only_religious_schools': True,
                'static': True,
                'same_price_for_all': False,
                'class_ranges_max_prices': {
                    ('א', 'ד'): 0.0,
                    ('ה', 'ו'): 1770.0,
                    ('ז', 'ט'): 2120.0,
                    ('י', 'יב'): 2300.0
                },
                'price_for_one': {
                    ('ה', 'ו'): 177.0,
                    ('ז', 'ט'): 212.0,
                    ('י', 'יב'): 230.0
                }
            },
            {
                'name': 'תל"ן תורני חרדי',
                'only_religious_schools': True,
                'static': True,
                'same_price_for_all': False,
                'class_ranges_max_prices': {
                    ('א', 'ד'): 885.0,
                    ('ה', 'ו'): 1770.0,
                    ('ז', 'ט'): 2120.0,
                    ('י', 'יב'): 2300.0
                },
                'price_for_one': {
                    ('א', 'ו'): 177.0,
                    ('ז', 'ט'): 212.0,
                    ('י', 'יב'): 230.0
                }
            }
        ],
        'has_max_price': False,
    },
    'מרצון': {
        'clauses': [
            {
                'name': 'פעילות חברתית תורנית',
                'only_religious_schools': True,
                'static': True,
                'same_price_for_all': False,
                'class_ranges_max_prices': {
                    ('א', 'ו'): 250.0,
                    ('ז', 'יב'): 450.0
                }
            },
            {
                'name': 'העשרה מגמות',
                'only_religious_schools': False,
                'static': False,
                'same_price_for_all': False,
                'max_price_func': megamot_max_price
            }
        ],
        'has_max_price': True,
        'static': True,
        'same_price_for_all': False,
        'class_ranges_max_prices': {
            ('א', 'ו'): 250.0,
            ('ז', 'יב'): 450.0
        }
    }
}

""" 
    This function sums all clauses to get max price for the payment type.
    For some payment types(meratzon), there is a max price
    for the payment type itself but not for the clauses,
    so we can't just sum all the clauses max prices and
    output that as the max price. for these payment types,
    there is a max price for the payment type just like
    the payment clauses(static, same_price_for_all, etc).
"""


def get_payment_type_max_price(class_id, payment_type, payment_clauses):
    payment_type_max_price = 0
    try:
        payment_type_dict = PAYMENTS_MAX_PRICES[payment_type]
    except KeyError:
        # Can't charge for a type that doesn't exist..
        return 0
    has_max_price = payment_type_dict['has_max_price']
    if has_max_price:
        # For now, all payment types with max price are static
        return _get_static_max_price(payment_type_dict, class_id)
    else:
        return sum(clause['max_price'] for clause in payment_clauses)


def find_clauses_by_names(payment_type, clause_names):
    clauses = []
    try:
        all_payment_type_clauses = PAYMENTS_MAX_PRICES[payment_type]['clauses']
    except:
        # No such payment type
        return clauses
    for clause_name in clause_names:
        matching_clauses = (clause for clause in all_payment_type_clauses if clause[
                            "name"] == clause_name)
        clauses.append(next(matching_clauses, None))
    return clauses


def get_clause_max_price(school, class_id, clause):
    is_static = clause["static"]
    if is_static:
        price = _get_static_max_price(clause, class_id)
        return price
    else:
        clause_max_price_func = clause["max_price_func"]
        return clause_max_price_func(school, class_id)


def _get_static_max_price(payment_type_or_clause, class_id):
    is_same_price_for_all = payment_type_or_clause['same_price_for_all']
    if is_same_price_for_all:
        return payment_type_or_clause['max_price']
    return _get_class_price(
        class_id, payment_type_or_clause['class_ranges_max_prices'])

"""
Some payment clauses have prices for a single hour,
for example: price for a single talan hour, price for a single
seminarion, etc. This function returns that price, similar to 
_get_static_max_price.
"""


def get_price_for_one(class_id, payment_clause):
    if payment_clause is not None and 'price_for_one' in payment_clause:
        return _get_class_price(
            class_id, payment_clause['price_for_one'])


def _get_class_price(class_id, class_ranges_prices):
    class_id_range = ()
    for class_range, price in class_ranges_prices.items():
        first_class_id = get_class_id(class_range[0])
        # Two types of class ranges - either from one class to another,
        # or a single class
        if len(class_range) == 2:
            # +1 since inclusive, same in second range type
            second_class_id = get_class_id(class_range[1])
            class_id_range = first_class_id, second_class_id + 1
        elif len(class_range) == 1:
            class_id_range = first_class_id, first_class_id + 1
        if class_id in range(*class_id_range):
            return price
    return 0.0
