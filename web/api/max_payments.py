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
        # the models.py TODO: fix without a hack.
        return MESIBAT_SIUM_MAX_PRICES['יסודי וחט"ב']

    print(school, class_id)
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
        'static': True,
        'same_price_for_all': True,
        'max_price': 75.0
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
            },
            {
                'name': 'סמינריון',
                'only_religious_schools': True,
                'static': True,
                'same_price_for_all': False,
                'class_ranges_max_prices': {
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
                }
            }
        ],
        # But can't write a max func because we can't refer to sum of
        # clauses(dict isn't self referential), since some of the clauses are
        # dynamic.
        'static': False,
        'same_price_for_all': False
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
                }
            }
        ],
        'static': False,
        'same_price_for_all': False
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
        'static': True,
        'same_price_for_all': False,
        'class_ranges_max_prices': {
            ('א', 'ו'): 250.0,
            ('ז', 'יב'): 450.0
        }
    }
}

""" 
    This function uses the max payments prices dict to calculate
    the max payment for a payment type in a class in a certain school. 
    school is also received as param because it is required for the
    dynamic functions in the max payments prices dict(see above).
    Why not just sum all this payment type clauses? 
    because in some cases, a school can overcharge a certian clause 
    but still be below the max price for the entire payment type.
    We want to know and be aware of that case, so we can't consider
    only a specific school's clauses. We need to know the max for
    the entire payment type.
"""


def get_payment_type_max_price(school, class_id, payment_type):
    payment_type_max_price = 0
    try:
        payment_type_dict = PAYMENTS_MAX_PRICES[payment_type]
    except KeyError:
        # Can't charge for a type that doesn't exist..
        return 0

    is_static = payment_type_dict['static']
    if is_static:
        return _get_static_max_price(payment_type_dict, class_id)
    else:
        payment_type_clauses = payment_type_dict['clauses']
        clauses_max_payments = [get_clause_max_price(school, class_id, clause)
                                for clause in payment_type_clauses
                                ]
        return sum(clauses_max_payments)


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
    return _get_class_max_price(
        class_id, payment_type_or_clause['class_ranges_max_prices'])


def _get_class_max_price(class_id, class_ranges_max_prices):
    class_id_range = ()
    for class_range, max_price in class_ranges_max_prices.items():
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
            return max_price
    return 0.0
