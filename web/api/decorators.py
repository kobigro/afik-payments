import functools
from flask import jsonify, request, make_response, current_app
from datetime import timedelta

def json(**kwargs):
    """This decorator generates a JSON response from a Python dictionary or
    a SQLAlchemy model."""
    key_name = kwargs.get('key_name')

    def json_decorator(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            rv = f(*args, **kwargs)
            status_or_headers = None
            headers = None
            if isinstance(rv, tuple):
                rv, status_or_headers, headers = rv + (None,) * (3 - len(rv))
            if isinstance(status_or_headers, (dict, list)):
                headers, status_or_headers = status_or_headers, None
            if isinstance(rv, list):
                rv = [obj.json() if hasattr(obj, 'json')
                      else obj for obj in rv]
            elif not isinstance(rv, dict):
                rv = obj.json()

            rv = jsonify({key_name: rv}) if key_name else jsonify(rv)
            if status_or_headers is not None:
                rv.status_code = status_or_headers
            if headers is not None:
                rv.headers.extend(headers)
            return rv
        return wrapped
    return json_decorator


def crossdomain(origin="*", methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None:
        headers = ', '.join(x.upper() for x in headers)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp
        f.provide_automatic_options = False
        return functools.update_wrapper(wrapped_function, f)
    return decorator
