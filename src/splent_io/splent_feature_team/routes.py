from flask import abort, current_app, render_template

from splent_io.splent_feature_team import team_bp
from splent_framework.services.service_locator import service_proxy

team_service = service_proxy("TeamService")


@team_bp.route("/team", methods=["GET"])
def index():
    # Group order is declared per product via TEAM_GROUPS (the role/section
    # types). Groups listed there come first, in that order; any others follow.
    grouped = team_service.grouped()
    order = current_app.config.get("TEAM_GROUPS", [])
    ordered = {g: grouped.pop(g) for g in order if g in grouped}
    ordered.update(grouped)
    return render_template("team/list.html", groups=ordered)


@team_bp.route("/team/<slug>", methods=["GET"])
def detail(slug):
    member = team_service.get_by_slug(slug)
    if member is None:
        abort(404)
    return render_template("team/detail.html", member=member)
