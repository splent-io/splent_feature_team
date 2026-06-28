import re

from flask import (
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import login_required

from splent_io.splent_feature_team import team_bp
from splent_io.splent_feature_team.models import Role, TeamMember
from splent_framework.db import db
from splent_framework.services.service_locator import service_proxy

team_service = service_proxy("TeamService")


# =====================================================================
# PUBLIC
# =====================================================================
@team_bp.route("/team", methods=["GET"])
def index():
    return render_template("team/list.html", groups=team_service.grouped())


@team_bp.route("/team/<slug>", methods=["GET"])
def detail(slug):
    member = team_service.get_by_slug(slug)
    if member is None:
        abort(404)
    return render_template("team/detail.html", member=member)


# =====================================================================
# Helpers
# =====================================================================
def _slugify(value):
    base = re.sub(r"[^a-z0-9]+", "-", (value or "").lower()).strip("-")
    return base or "item"


def _unique_slug(model, value, exclude_id=None):
    base = _slugify(value)
    slug, i = base, 2
    while True:
        q = model.query.filter_by(slug=slug)
        if exclude_id:
            q = q.filter(model.id != exclude_id)
        if not q.first():
            return slug
        slug, i = f"{base}-{i}", i + 1


def _member_form_to_data(form):
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
        "position": (form.get("position") or "").strip(),
        "affiliation": (form.get("affiliation") or "").strip(),
        "email": (form.get("email") or "").strip(),
        "photo": (form.get("photo") or "").strip(),
        "link": (form.get("link") or "").strip(),
        "bio": (form.get("bio") or "").strip(),
        "links": links,
        "order": int(form.get("order") or 0),
        "published": "published" in form,
    }


def _apply_roles(member, form):
    ids = [int(x) for x in form.getlist("roles") if x]
    member.roles = Role.query.filter(Role.id.in_(ids)).all() if ids else []


# =====================================================================
# ADMIN — members
# =====================================================================
@team_bp.route("/admin/team", methods=["GET"])
@login_required
def admin_index():
    roles = team_service.roles()
    groups = {
        role: sorted(role.members, key=lambda m: (m.order, m.name)) for role in roles
    }
    unassigned = [
        m
        for m in TeamMember.query.order_by(
            TeamMember.order.asc(), TeamMember.name.asc()
        ).all()
        if not m.roles
    ]
    return render_template(
        "team/admin/list.html", groups=groups, unassigned=unassigned, roles=roles
    )


@team_bp.route("/admin/team/new", methods=["GET", "POST"])
@login_required
def admin_new():
    if request.method == "POST":
        data = _member_form_to_data(request.form)
        if not data["name"]:
            flash("Name is required.", "danger")
            return redirect(url_for("team.admin_new"))
        data["slug"] = _unique_slug(TeamMember, data["name"])
        member = TeamMember(**data)
        _apply_roles(member, request.form)
        db.session.add(member)
        db.session.commit()
        flash(f"Added {member.name}.", "success")
        return redirect(url_for("team.admin_index"))
    return render_template(
        "team/admin/form.html", member=None, roles=team_service.roles()
    )


@team_bp.route("/admin/team/<int:member_id>/edit", methods=["GET", "POST"])
@login_required
def admin_edit(member_id):
    member = TeamMember.query.get_or_404(member_id)
    if request.method == "POST":
        data = _member_form_to_data(request.form)
        if not data["name"]:
            flash("Name is required.", "danger")
            return redirect(url_for("team.admin_edit", member_id=member_id))
        if data["name"] != member.name:
            data["slug"] = _unique_slug(TeamMember, data["name"], exclude_id=member.id)
        for key, value in data.items():
            setattr(member, key, value)
        _apply_roles(member, request.form)
        db.session.commit()
        flash(f"Updated {member.name}.", "success")
        return redirect(url_for("team.admin_index"))
    return render_template(
        "team/admin/form.html", member=member, roles=team_service.roles()
    )


@team_bp.route("/admin/team/<int:member_id>/delete", methods=["POST"])
@login_required
def admin_delete(member_id):
    member = TeamMember.query.get_or_404(member_id)
    name = member.name
    db.session.delete(member)
    db.session.commit()
    flash(f"Removed {name}.", "success")
    return redirect(url_for("team.admin_index"))


# =====================================================================
# ADMIN — roles
# =====================================================================
@team_bp.route("/admin/team/roles", methods=["GET", "POST"])
@login_required
def admin_roles():
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        if name:
            db.session.add(
                Role(
                    name=name,
                    slug=_unique_slug(Role, name),
                    order=int(request.form.get("order") or 0),
                )
            )
            db.session.commit()
            flash(f"Created role “{name}”.", "success")
        return redirect(url_for("team.admin_roles"))
    return render_template("team/admin/roles.html", roles=team_service.roles())


@team_bp.route("/admin/team/roles/<int:role_id>/edit", methods=["POST"])
@login_required
def admin_role_edit(role_id):
    role = Role.query.get_or_404(role_id)
    name = (request.form.get("name") or "").strip()
    if name:
        role.name = name
        role.order = int(request.form.get("order") or role.order or 0)
        db.session.commit()
        flash("Role updated.", "success")
    return redirect(url_for("team.admin_roles"))


@team_bp.route("/admin/team/roles/<int:role_id>/delete", methods=["POST"])
@login_required
def admin_role_delete(role_id):
    role = Role.query.get_or_404(role_id)
    name = role.name
    db.session.delete(role)  # cascade clears the pivot rows
    db.session.commit()
    flash(f"Removed role “{name}”.", "success")
    return redirect(url_for("team.admin_roles"))
