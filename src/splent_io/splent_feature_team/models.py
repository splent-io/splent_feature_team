from splent_framework.db import db


class TeamMember(db.Model):
    """A person in the directory — organiser, faculty member, speaker, PhD…"""

    __tablename__ = "team_member"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), nullable=False, unique=True, index=True)
    role = db.Column(db.String(255), default="")
    affiliation = db.Column(db.String(255), default="")
    group = db.Column(db.String(128), default="Team")  # section bucket: Organizers, Faculty, PhD…
    bio = db.Column(db.Text, default="")
    photo = db.Column(db.String(512), default="")
    email = db.Column(db.String(255), default="")
    link = db.Column(db.String(512), default="")
    links = db.Column(db.JSON, default=list)  # [{"label": "ORCID", "url": "…"}, …]
    order = db.Column(db.Integer, default=0)
    published = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"TeamMember<{self.slug}>"
