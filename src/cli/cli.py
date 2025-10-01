import click
import sys
import logging

from core.storage.WavesLabRepository import repository

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version='1.0.0')
def waveslab():
    """
    WavesLab Simulation Environment CLI

    Control WaveNodes and manage virtual users in the household simulation.
    """
    pass

@waveslab.command()
@click.argument('node_id')
@click.option('--user', '-u', help='Associate a user with this node')
def start(node_id: str, user: str = None):
    """
    Start a WaveNode by id.

    id: The id of the WaveNode to start

    Examples:
        waveslab start "living-room-light"
        waveslab start "kitchen-faucet" --user alice
    """
    try:
        success, message = repository.start_node(node_id, user)

        if success:
            click.echo(message)
            sys.exit(0)
        else:
            click.echo(f"Error: {message}", err=True)
            sys.exit(1)

    except Exception as e:
        logger.error(f"Unexpected error starting node '{node_id}': {e}")
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)

@waveslab.command()
@click.argument('node_id')
def stop(node_id: str):
    """
    Stop a WaveNode by id.

    id: The id of the WaveNode to stop

    Examples:
        waveslab stop "living-room-light"
        waveslab stop "kitchen-faucet"
    """
    try:
        success, message = repository.stop_node(node_id)

        if success:
            click.echo(message)
            sys.exit(0)
        else:
            click.echo(f"Error: {message}", err=True)
            sys.exit(1)

    except Exception as e:
        logger.error(f"Unexpected error starting node '{node_id}': {e}")
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@waveslab.command()
def status():
    try:
        nodes = repository.get_all_nodes()
        if not nodes:
            click.echo("No WaveNodes found.")
            return

        click.echo("\nWaveNodes:")
        click.echo("-" * 60)

        for node in nodes:
            click.echo(f"{node.status.lower()} - {node.name}")
    except Exception as e:
        logger.error(f"Error listing nodes: {e}")
        click.echo(f"Error listing nodes: {e}", err=True)
        sys.exit(1)

@waveslab.command()
def users():
    """
    List all VirtualUsers in the system.
    """
    try:
        list_of_users = repository.get_all_users()

        if not list_of_users:
            click.echo("No VirtualUsers found.")
            return

        click.echo("\nVirtual Users:")
        click.echo("-" * 30)

        for user in list_of_users:
            click.echo(f"• {user.username}")

    except Exception as e:
        logger.error(f"Error listing users: {e}")
        click.echo(f"Error listing users: {e}", err=True)
        sys.exit(1)