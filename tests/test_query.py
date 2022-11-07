import asyncio

import pytest

from sircle.query import Config, Query

config = Config(from_env=True)


@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.mark.asyncio
async def test_create():
    """Test the functionality of CREATE.

    Create an entry in the database.
    """
    create_query = Query(config=config)
    table_name = "person"
    cont = {
        "name": "Tobie",
        "company": "SurrealDB",
        "skills": ["Rust", "Go", "JavaScript"],
    }
    create_query.create(table_name).content(cont)
    res = await create_query.execute()
    assert res[0]["id"].split(":")[0] == table_name
    assert res[0]["company"] == cont["company"]
    assert res[0]["skills"] == cont["skills"]
    assert res[0]["name"] == cont["name"]


@pytest.mark.asyncio
@pytest.mark.dependency(on=["test_create"])
async def test_select():
    """Test the functionality of CREATE by looking in the database."""
    query = Query(config=config)
    query.select(["name", "company", "skills"]).from_("person")
    res = await query.execute()
    assert res[0]["company"] == "SurrealDB"
    assert res[0]["skills"] == ["Rust", "Go", "JavaScript"]
    assert res[0]["name"] == "Tobie"


@pytest.mark.asyncio
async def test_insert():
    """Test the functionality of INSERT.

    Create an entry in the database.
    """
    insert_query = Query(config=config)
    table_name = "person (name, company, founded)"
    data = tuple(["John", "SurrealDB", "2021-09-10"])
    insert_query.insert(table_name, values=data)
    res = await insert_query.execute()
    assert res[0]["id"].split(":")[0] == table_name.split(" ")[0]
    assert res[0]["company"] == "SurrealDB"
    assert res[0]["founded"] == "2021-09-10T00:00:00Z"
    assert res[0]["name"] == "John"


@pytest.mark.asyncio
@pytest.mark.dependency(on=["test_insert"])
async def test_select2():
    """Test the functionality of INSERT by looking in the database."""
    query = Query(config=config)
    query.select("*").from_("person")
    res = await query.execute()
    assert res[0]["company"] == "SurrealDB"
    assert res[0]["founded"] == "2021-09-10T00:00:00Z"
    assert res[0]["name"] == "John"
    assert res[0]["id"].split(":")[0] == "person"
