from splent_framework.blueprints.base_blueprint import create_blueprint
from splent_framework.nav.nav_registry import register_nav_item
from splent_framework.services.service_locator import register_service

from splent_io.splent_feature_team.services import TeamService

team_bp = create_blueprint(__name__)


def init_feature(app):
    # Team is managed through its OWN custom admin screens (see routes.py and
    # hooks.py) — the WordPress-plugin pattern — instead of the generic admin
    # resource, so it does not call register_admin_resource.
    register_service(app, "TeamService", TeamService)
    register_nav_item(key="team", label="Team", href="/team", order=40)


def inject_context_vars(app):
    return {}
