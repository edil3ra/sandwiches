from functools import wraps
from flask import abort
from flask_login import current_user
from .models import User


def admin_required(f):
    @wraps(f)
    def decorater(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorator


def manager_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if not current_user.is_manager:
            abort(403)
        return f(*args, **kwargs)
    return decorator


def employee_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if not current_user.is_employee:
            abort(403)
        return f(*args, **kwargs)
    return decorator


