# Copyright 2019 Contributors to Hyperledger Sawtooth
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------
"""Utility functions to assist with tests in cleanup or running."""
from time import sleep
import rethinkdb as r
from rbac.providers.common.db_queries import connect_to_db
from rbac.common.logs import get_default_logger

LOGGER = get_default_logger(__name__)


def create_test_role(session, role_payload):
    """Create a role and authenticate to use api endpoints during testing."""
    response = session.post("http://rbac-server:8000/api/roles", json=role_payload)
    sleep(3)
    return response


def create_test_task(session, task_payload):
    """Create a task and authenticate to use api endpoints during testing."""
    response = session.post("http://rbac-server:8000/api/tasks", json=task_payload)
    sleep(3)
    return response


def create_test_user(session, user_payload):
    """Create a user and authenticate to use api endpoints during testing."""
    response = session.post("http://rbac-server:8000/api/users", json=user_payload)
    sleep(3)
    return response


def delete_user_by_username(username):
    """Delete a user from db by the username."""
    conn = connect_to_db()
    r.table("users").filter({"username": username}).delete().run(conn)
    r.table("auth").filter({"username": username}).delete().run(conn)
    conn.close()


def delete_role_by_name(name):
    """Delete a role from db by the name."""
    conn = connect_to_db()
    try:
        role_id = r.table("roles").filter({"name": name}).coerce_to("array").run(conn)
        r.table("roles").filter({"name": name}).delete().run(conn)
        r.table("role_owners").filter({"role_id": role_id[0]["role_id"]}).delete().run(
            conn
        )
        r.table("role_members").filter({"role_id": role_id[0]["role_id"]}).delete().run(
            conn
        )
        r.table("role_admins").filter({"role_id": role_id[0]["role_id"]}).delete().run(
            conn
        )
        r.table("role_tasks").filter({"role_id": role_id[0]["role_id"]}).delete().run(
            conn
        )
        conn.close()
    except KeyError:
        conn.close()


def delete_pack_by_name(name):
    """Delete a pack from db by the name."""
    conn = connect_to_db()
    pack_id = r.table("packs").filter({"name": name}).coerce_to("array").run(conn)
    r.table("packs").filter({"name": name}).delete().run(conn)
    r.table("pack_owners").filter({"pack_id": pack_id[0]["pack_id"]}).delete().run(conn)
    r.table("role_packs").filter({"identifiers": [pack_id[0]["pack_id"]]}).delete().run(
        conn
    )
    conn.close()


def delete_task_by_name(name):
    """Delete a task from db by the name."""
    conn = connect_to_db()
    task_id = r.table("tasks").filter({"name": name}).coerce_to("array").run(conn)
    r.table("tasks").filter({"name": name}).delete().run(conn)
    r.table("task_owners").filter({"task_id": task_id[0]["task_id"]}).delete().run(conn)
    r.table("role_tasks").filter({"identifiers": [task_id[0]["task_id"]]}).delete().run(
        conn
    )
    conn.close()


def insert_role(role_data):
    """Inserting a role to the database"""
    conn = connect_to_db()
    r.table("roles").insert(role_data).run(conn)
    conn.close()


def insert_user(user_data):
    """Inserting a user to the database"""
    conn = connect_to_db()
    r.table("users").insert(user_data).run(conn)
    conn.close()


def get_proposal_with_retry(session, proposal_id):
    """Gets proposal via proposal API, retries 4 times."""
    retry = 0
    max_retries = 4
    while True:
        response = session.get(
            "http://rbac-server:8000/api/proposals/{}".format(proposal_id)
        )
        if response.status_code == 200:
            break
        elif retry > max_retries:
            break
        else:
            retry += 1
            LOGGER.info("retrying get proposal... %s", retry)
            sleep(5)
    return response
