from splent_framework.admin import register_admin_resource
from splent_framework.blueprints.base_blueprint import create_blueprint
from splent_framework.services.service_locator import register_service

from splent_io.splent_feature_team.models import TeamMember
from splent_io.splent_feature_team.services import TeamService

team_bp = create_blueprint(__name__)


def init_feature(app):
    register_service(app, "TeamService", TeamService)

    register_admin_resource(
        TeamMember,
        name="team_member",
        label="Team member",
        label_plural="Team",
        icon="users",
        group="People",
        order=10,
        list_columns=["name", "role", "group", "order"],
        field_widgets={
            "bio": "richtext",
            "photo": "image",
            "email": "text",
            "link": "url",
            "slug": "slug",
            "published": "bool",
        },
        feature="team",
    )


def inject_context_vars(app):
    return {}
