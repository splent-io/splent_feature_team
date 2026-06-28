from flask import request, url_for

from splent_framework.hooks.template_hooks import register_template_hook


def team_admin_link():
    """Sidebar entry for the Team management screen (the WP-plugin pattern)."""
    active = (
        "active"
        if request.endpoint and request.endpoint.startswith("team.admin")
        else ""
    )
    return (
        f'<li class="sidebar-item {active}">'
        f'<a class="sidebar-link" href="{url_for("team.admin_index")}">'
        '<i class="align-middle" data-feather="users"></i> '
        '<span class="align-middle">Team</span>'
        "</a>"
        "</li>"
    )


register_template_hook("layout.authenticated_sidebar", team_admin_link)
