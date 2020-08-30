from flask import render_template
from project import app


@app.errorhandler(404)
def not_found_error(error):
    '''
    Handles 404 errors.
    '''
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    '''
    Handles 500 errors.
    '''
    return render_template('500.html'), 500