from splent_framework.seeders.BaseSeeder import BaseSeeder

from splent_io.splent_feature_team.models import TeamMember


class TeamSeeder(BaseSeeder):
    def run(self):
        self.seed(
            [
                TeamMember(
                    slug="david-benavides", name="David Benavides", role="Director",
                    group="Faculty", affiliation="Universidad de Sevilla", order=1,
                    bio="<p>Professor and director of Diverso Lab.</p>",
                ),
                TeamMember(
                    slug="jose-galindo", name="José A. Galindo", role="Researcher",
                    group="Faculty", affiliation="Universidad de Sevilla", order=2,
                ),
                TeamMember(
                    slug="organising-committee", name="Organising Committee",
                    role="Students", group="Organisers",
                    affiliation="ETSII · University of Seville", order=3,
                    bio="<p>The student team behind InnoSoft Days.</p>",
                ),
            ]
        )
