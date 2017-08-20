from flask import render_template, request
from flask import current_app


@current_app.errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403


# @current_app.errorhandler(404)
# def page_not_found(e):
#     return render_template('errors/404_manager.html'), 404


@current_app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500
