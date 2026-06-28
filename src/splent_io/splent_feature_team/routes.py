import re

from flask import (
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import login_required

from splent_io.splent_feature_team import team_bp
from splent_io.splent_feature_team.models import TeamMember
from splent_framework.db import db
from splent_framework.services.service_locator import service_proxy

team_service = service_proxy("TeamService")


# =====================================================================
# PUBLIC
# =====================================================================
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


# =====================================================================
# ADMIN — domain-specific management (the "plugin" screen)
# =====================================================================
def _slugify(value):
    base = re.sub(r"[^a-z0-9]+", "-", (value or "").lower()).strip("-")
    return base or "member"


def _unique_slug(name, exclude_id=None):
    base = _slugify(name)
    slug, i = base, 2
    while True:
        q = TeamMember.query.filter_by(slug=slug)
        if exclude_id:
            q = q.filter(TeamMember.id != exclude_id)
        if not q.first():
            return slug
        slug, i = f"{base}-{i}", i + 1


def _ordered_groups():
    """All members (incl. drafts) grouped; TEAM_GROUPS first, extras after."""
    grouped = {}
    for m in TeamMember.query.order_by(
        TeamMember.order.asc(), TeamMember.name.asc()
    ).all():
        grouped.setdefault(m.group or "Team", []).append(m)
    order = current_app.config.get("TEAM_GROUPS", [])
    ordered = {g: grouped.pop(g) for g in order if g in grouped}
    ordered.update(grouped)
    return ordered


def _known_groups():
    cfg = list(current_app.config.get("TEAM_GROUPS", []))
    existing = [
        g[0] for g in db.session.query(TeamMember.group).distinct().all() if g[0]
    ]
    seen, out = set(), []
    for g in cfg + existing:
        if g and g not in seen:
            seen.add(g)
            out.append(g)
    return out


def _form_to_data(form):
    links = []
    for line in (form.get("links") or "").splitlines():
        line = line.strip()
        if not line:
            continue
        if "|" in line:
            label, url = line.split("|", 1)
            links.append({"label": label.strip(), "url": url.strip()})
        else:
            links.append({"label": "Link", "url": line})
    return {
        "name": (form.get("name") or "").strip(),
        "role": (form.get("role") or "").strip(),
        "affiliation": (form.get("affiliation") or "").strip(),
        "group": (form.get("group") or "Team").strip() or "Team",
        "email": (form.get("email") or "").strip(),
        "photo": (form.get("photo") or "").strip(),
        "link": (form.get("link") or "").strip(),
        "bio": (form.get("bio") or "").strip(),
        "links": links,
        "order": int(form.get("order") or 0),
        "published": bool(form.get("published")),
    }


@team_bp.route("/admin/team", methods=["GET"])
@login_required
def admin_index():
    return render_template(
        "team/admin/list.html",
        groups=_ordered_groups(),
        known_groups=_known_groups(),
    )


@team_bp.route("/admin/team/new", methods=["GET", "POST"])
@login_required
def admin_new():
    if request.method == "POST":
        data = _form_to_data(request.form)
        if not data["name"]:
            flash("Name is required.", "danger")
            return redirect(url_for("team.admin_new"))
        data["slug"] = _unique_slug(data["name"])
        db.session.add(TeamMember(**data))
        db.session.commit()
        flash(f"Added {data['name']}.", "success")
        return redirect(url_for("team.admin_index"))
    return render_template(
        "team/admin/form.html", member=None, known_groups=_known_groups()
    )


@team_bp.route("/admin/team/<int:member_id>/edit", methods=["GET", "POST"])
@login_required
def admin_edit(member_id):
    member = TeamMember.query.get_or_404(member_id)
    if request.method == "POST":
        data = _form_to_data(request.form)
        if not data["name"]:
            flash("Name is required.", "danger")
            return redirect(url_for("team.admin_edit", member_id=member_id))
        if data["name"] != member.name:
            data["slug"] = _unique_slug(data["name"], exclude_id=member.id)
        for key, value in data.items():
            setattr(member, key, value)
        db.session.commit()
        flash(f"Updated {member.name}.", "success")
        return redirect(url_for("team.admin_index"))
    return render_template(
        "team/admin/form.html", member=member, known_groups=_known_groups()
    )


@team_bp.route("/admin/team/<int:member_id>/move", methods=["POST"])
@login_required
def admin_move(member_id):
    member = TeamMember.query.get_or_404(member_id)
    new_group = (request.form.get("group") or "").strip()
    if new_group and new_group != member.group:
        member.group = new_group
        db.session.commit()
        flash(f"Moved {member.name} to {new_group}.", "success")
    return redirect(url_for("team.admin_index"))


@team_bp.route("/admin/team/<int:member_id>/delete", methods=["POST"])
@login_required
def admin_delete(member_id):
    member = TeamMember.query.get_or_404(member_id)
    name = member.name
    db.session.delete(member)
    db.session.commit()
    flash(f"Removed {name}.", "success")
    return redirect(url_for("team.admin_index"))
