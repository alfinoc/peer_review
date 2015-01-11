from werkzeug.serving import run_simple
from peer_review_wsgi import create_app
# for debugging/development, set use_debugger=True, use_reloader=True,
run_simple('localhost', 5000, create_app(), use_debugger=True, use_reloader=True)
