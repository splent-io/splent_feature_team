"""
CLI commands contributed by splent_feature_team.

These commands are auto-discovered by the framework and exposed in the
SPLENT CLI under the ``feature:team`` group.

Usage::

    splent feature:team hello
"""

import click


@click.command("hello")
def hello():
    """Example command — replace with your own."""
    click.echo("  Hello from splent_feature_team!")


cli_commands = [hello]
