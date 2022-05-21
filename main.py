import os
import click
import uvicorn

import commands.users
import server
from commands import *
from starlette.applications import Starlette
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from exceptions import RegisterException

import example
from database import database
from rooms import rooms_service
from users import users_service


def set_user_login(obj, login, password):
    with obj['db']:
        cursor = obj['db'].cursor()
        user = users_service.login(cursor, login, password)
        if user is None:
            print("Wrong credentials!")
            exit(1)

        obj['user'] = user

@click.group()
@click.pass_context
def run_command(ctx):
    ctx.obj = {
        'db': database.get_database(
            os.path.join(
                os.path.dirname(
                    os.path.abspath(__name__)
                ), "db.sqlite")
        )
    }



# @user_command.group("login")
# @click.option("--login", required=True, prompt=True)
# @click.password_option(confirmation_prompt=False)
# @click.pass_obj
# def login_command(obj, login, password):
#     set_user_login(obj, login, password)
#


@run_command.group('user')
def user_command():
    pass

@user_command.command('register')
@click.option("--login", required=True, prompt=True)
@click.password_option()
@click.pass_obj
def register_command(obj, login, password):
    try:
        commands.users.register_command(login, password)
    except RegisterException as e:
        click.echo(e.args[0])


@user_command.group("login")
@click.option("--login", required=True, prompt=True)
@click.password_option(confirmation_prompt=False)
@click.pass_obj
def login_command(obj, login, password):
    set_user_login(obj, login, password)


@login_command.command("list")
@click.pass_obj
@click.option("--filter", required=False)
def list_command(obj, filter):
    for user in users_service.get_all_users(obj['db'].cursor()):
        if filter is None:
            print(user.login)
        elif user.login.find(filter) > -1:
            print(user.login)


@login_command.command("remove")
@click.pass_obj
@click.option("--login-to-remove", required=True, prompt=True)
def remove_command(obj, login):
    with obj['db']:
        users_service.remove_user(obj['db'].cursor(), login)


@run_command.group('run')
def server_command():
    pass


@server_command.command("as_server")
def start_server():
    app = Starlette(debug=True, routes=server.routes)
    uvicorn.run(app, host="127.0.0.1", port=5000, log_level="info")


@run_command.group('db')
def db_command():
    pass


@db_command.command('initialize')
@click.pass_obj
def initialize_command(obj):
    database.initialize(obj['db'])


@run_command.group('room')
@click.option("--login", required=True, prompt=True)
@click.password_option(confirmation_prompt=False)
@click.pass_obj
def rooms_command(obj, login, password):
    set_user_login(obj, login, password)


@rooms_command.command('create')
@click.password_option("--room-password", confirmation_prompt=True)
@click.pass_obj
def create_command(obj, room_password):
    with obj['db']:
        rooms_service.create_room(obj['db'].cursor(), obj['user'].id, room_password)


@rooms_command.command("delete")
@click.option("--room-id", required=True, prompt=True, type=click.types.INT)
@click.pass_obj
def delete_room_command(obj, room_id):
    with obj['db']:
        cursor = obj['db'].cursor()

        room = rooms_service.get_room(cursor, room_id)
        if room is None:
            print("Wrong room id!")
            exit(1)

        if room.owner_id != obj['user'].id:
            print("Wrong room id!")
            exit(1)

        rooms_service.delete_room_by_id(cursor, room_id)


@rooms_command.command("join")
@click.option("--room-id", required=True, prompt=True, type=click.types.INT)
@click.password_option("--room-password", confirmation_prompt=False)
@click.pass_obj
def join_room_command(obj, room_id, room_password):
    with obj['db']:
        if not rooms_service.join_room(obj['db'].cursor(), obj['user'].id, room_id, room_password):
            print("Wrong room id or passowrd!")
            exit(1)


@rooms_command.command("set-topic")
@click.option("--room-id", required=True, prompt=True, type=click.types.INT)
@click.option("--new-topic", required=True, prompt=True)
@click.pass_obj
def set_topic_command(obj, room_id, new_topic):
    with obj['db']:
        cursor = obj['db'].cursor()
        room = rooms_service.get_room(cursor, room_id)
        if room is None:
            print("Unknown room!")
            exit(1)

        if room.owner_id != obj['user'].id:
            print("Unknown room!")
            exit(1)

        topic = rooms_service.get_topic(cursor, room_id)
        if topic is not None:
            rooms_service.remove_all_votes(cursor, topic.id)
            rooms_service.remove_topic(cursor, room_id)

        rooms_service.create_topic(cursor, room_id, new_topic)


@rooms_command.command("vote")
@click.option("--topic-id", required=True, prompt=True, type=click.types.INT)
@click.option("--value", required=True, prompt=True, type=click.types.FLOAT)
@click.pass_obj
def vote_command(obj, topic_id, value):
    with obj['db']:
        cursor = obj['db'].cursor()
        topic = rooms_service.get_topic_by_id(cursor, topic_id)
        if topic is None:
            print("Wrong topic!")
            exit(1)

        if not rooms_service.joined_room(cursor, obj['user'].id, topic.room_id):
            print("Wrong topic!")
            exit(1)

        rooms_service.add_vote(cursor, topic_id, value, obj['user'].id)


db_path = os.path.join(os.path.dirname(os.path.abspath(__name__)), "db.sqlite")

if __name__ == "__main__":
    run_command()

