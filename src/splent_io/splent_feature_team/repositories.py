from __future__ import annotations

from splent_io.splent_feature_team.models import TeamMember
from splent_framework.repositories.BaseRepository import BaseRepository


class TeamRepository(BaseRepository):
    def __init__(self):
        super().__init__(TeamMember)

    def list_published(self) -> list[TeamMember]:
        return (
            TeamMember.query.filter_by(published=True)
            .order_by(TeamMember.order.asc(), TeamMember.name.asc())
            .all()
        )

    def get_by_slug(self, slug: str) -> TeamMember | None:
        return TeamMember.query.filter_by(slug=slug).first()

    def grouped(self) -> dict[str, list[TeamMember]]:
        groups: dict[str, list[TeamMember]] = {}
        for member in self.list_published():
            groups.setdefault(member.group, []).append(member)
        return groups
