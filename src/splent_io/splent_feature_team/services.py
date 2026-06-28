from splent_io.splent_feature_team.models import Role
from splent_io.splent_feature_team.repositories import TeamRepository
from splent_framework.services.BaseService import BaseService


class TeamService(BaseService):
    def __init__(self):
        super().__init__(TeamRepository())

    def grouped(self):
        return self.repository.grouped()

    def get_by_slug(self, slug):
        return self.repository.get_by_slug(slug)

    def roles(self):
        return Role.query.order_by(Role.order.asc(), Role.name.asc()).all()
