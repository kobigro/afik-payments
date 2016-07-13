from errors import NotFoundError
from models import School, SchoolPayment
from sqlalchemy import func
from utils import get_class_id
import max_payments
from itertools import zip_longest


def get_payments(school_id, class_name=None):
    school = School.query.get(school_id)
    if school is None:
        raise NotFoundError("school not found")
    class_id = get_class_id(class_name)
    if class_id is None or not school.has_class(class_id):
        raise NotFoundError("class not found")
    return _get_payments(school, class_id)


def _get_payments(school, class_id):
    query = school.payments.filter_by(of_class=class_id)
    a = _group_by(query.all(), 'type')
    payments = []
    for payment_type, payment_type_clauses in a.items():
        payment_type_price = sum(
            [clause.price for clause in payment_type_clauses])
        # only if charging for this payment type
        if payment_type_price > 0:
            payment_type_max_price = max_payments.get_payment_type_max_price(
                school, class_id, payment_type)
            clauses_with_max = get_clauses_with_max(payment_type, payment_type_clauses,
                                                    school, class_id)
            payment = {
                "type": payment_type,
                "price": payment_type_price,
                "max_price": payment_type_max_price,
                "clauses": clauses_with_max
            }
            payments.append(payment)
    return payments

""" 
    A helper function to get max payments for clauses. For each
    school clause payment, it returns a dict with the name, the price
    and the max price.
"""


def get_clauses_with_max(payment_type, clause_payments, school, class_id):
    clause_names = [payment.clause for payment in clause_payments]
    clauses_max_dicts = max_payments.find_clauses_by_names(
        payment_type, clause_names)
    clauses_with_max = []
    for clause_payment, clause_max_dict in zip(clause_payments, clauses_max_dicts):
        clause_price = clause_payment.price
        # only if charging for this clause
        if clause_price > 0:
            clause_max_price = max_payments.get_clause_max_price(
                school, class_id, clause_max_dict) if clause_max_dict is not None else None
            clauses_with_max.append(
                dict(name=clause_payment.clause,
                     price=clause_price, max_price=clause_max_price))
    return clauses_with_max


def _group_by(results, model_column_name):
    # A simple helper function for grouping sqlalchemy results.
    groups = {}
    for result in results:
        groups.setdefault(getattr(
            result, model_column_name), []).append(result)
    return groups
