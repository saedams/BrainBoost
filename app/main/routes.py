from app.main import bp
from app.main.main_routes import MainRoutes
from app.main.leerling import LeerlingRoutes

MainRoutes(bp)
LeerlingRoutes(bp)
