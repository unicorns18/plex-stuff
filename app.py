"""
This module is used to launch the application using the gunicorn WSGI server.
"""

from server_code import app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=1337, debug=True)
