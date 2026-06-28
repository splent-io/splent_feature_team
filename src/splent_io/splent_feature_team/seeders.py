import re

from splent_framework.db import db
from splent_framework.seeders.BaseSeeder import BaseSeeder

from splent_io.splent_feature_team.models import Role, TeamMember


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


class TeamSeeder(BaseSeeder):
    def run(self):
        roles = {}
        for i, name in enumerate(
            ["Faculty", "PhD & Master Students", "Organisers"], start=1
        ):
            role = Role(name=name, slug=_slug(name), order=i)
            db.session.add(role)
            roles[name] = role
        db.session.flush()

        members = [
            {
                "name": "David Benavides",
                "position": "Director",
                "affiliation": "Universidad de Sevilla",
                "bio": "<p>Professor and director of the lab.</p>",
                "roles": ["Faculty"],
            },
            {
                "name": "José A. Galindo",
                "position": "Researcher",
                "affiliation": "Universidad de Sevilla",
                "roles": ["Faculty"],
            },
            {
                "name": "Sample Student",
                "position": "PhD Student",
                "affiliation": "University of Seville",
                "roles": ["PhD & Master Students", "Organisers"],
            },
        ]
        objs = []
        for i, m in enumerate(members, start=1):
            tm = TeamMember(
                name=m["name"],
                slug=_slug(m["name"]),
                position=m["position"],
                affiliation=m.get("affiliation", ""),
                bio=m.get("bio", ""),
                order=i,
                published=True,
            )
            tm.roles = [roles[r] for r in m["roles"]]
            objs.append(tm)
        self.seed(objs)
