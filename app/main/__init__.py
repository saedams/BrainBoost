from flask import Blueprint
import importlib.util
import os

bp = Blueprint("main", __name__)

from app.main import routes

# Laad score routes
route_file = os.path.join(os.path.dirname(__file__), "route.score.py")
spec = importlib.util.spec_from_file_location("app.main.route.score", route_file)
route_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(route_module)

# Laad widget voorkeur routes
route_file = os.path.join(os.path.dirname(__file__), "route.widgets.py")
spec = importlib.util.spec_from_file_location("app.main.route.widgets", route_file)
route_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(route_module)
