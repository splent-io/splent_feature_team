from splent_framework.db import db


# Many-to-many association between team members and roles.
team_member_role = db.Table(
    "team_member_role",
    db.Column(
        "member_id",
        db.Integer,
        db.ForeignKey("team_member.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column(
        "role_id",
        db.Integer,
        db.ForeignKey("role.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Role(db.Model):
    """A team role / section a member can belong to.

    Examples: Faculty, PhD & Master Students, Organisers, Technical Staff.
    A member can hold several roles (many-to-many), so e.g. someone can be both
    Faculty and an Organiser. ``order`` drives the display order of sections.
    """

    __tablename__ = "role"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    slug = db.Column(db.String(128), nullable=False, unique=True, index=True)
    order = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"Role<{self.slug}>"


class TeamMember(db.Model):
    """A person in the directory.

    Their section membership is modelled as a many-to-many relation to
    :class:`Role` (``roles``). ``position`` is the free-text job title
    (e.g. "Full Professor"); it is NOT the section — sections are roles.
    """

    __tablename__ = "team_member"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), nullable=False, unique=True, index=True)
    position = db.Column(db.String(255), default="")  # job title, e.g. "Full Professor"
    affiliation = db.Column(db.String(255), default="")
    bio = db.Column(db.Text, default="")
    photo = db.Column(db.String(512), default="")
    email = db.Column(db.String(255), default="")
    link = db.Column(db.String(512), default="")
    links = db.Column(db.JSON, default=list)  # [{"label": "ORCID", "url": "…"}, …]
    order = db.Column(db.Integer, default=0)
    published = db.Column(db.Boolean, default=True)

    roles = db.relationship(
        "Role",
        secondary=team_member_role,
        backref=db.backref("members", lazy="dynamic"),
        order_by="Role.order",
        lazy="selectin",
    )

    def __repr__(self):
        return f"TeamMember<{self.slug}>"
