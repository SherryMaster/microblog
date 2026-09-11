from flask import render_template

from app import app, db


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    # A failed SQLAlchemy transaction leaves the session unusable until it is
    # rolled back.  The error template may touch application state, so reset
    # the session before rendering it.
    db.session.rollback()
    return render_template('500.html'), 500
