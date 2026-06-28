from __future__ import annotations

from splent_io.splent_feature_team.models import Role, TeamMember
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

    def roles(self) -> list[Role]:
        return Role.query.order_by(Role.order.asc(), Role.name.asc()).all()

    def grouped(self) -> dict[Role, list[TeamMember]]:
        """Published members grouped by role, roles ordered by ``Role.order``.

        A member holding several roles appears under each of them. Roles with no
        published members are skipped.
        """
        grouped: dict[Role, list[TeamMember]] = {}
        for role in self.roles():
            members = sorted(
                (m for m in role.members if m.published),
                key=lambda m: (m.order, m.name),
            )
            if members:
                grouped[role] = members
        return grouped
