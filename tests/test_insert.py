import asyncio

import pytest

from sirqle.query import Config, Query

config = Config(
    url="127.0.0.1:9120",
    namespace="test",
    database="test_insert",
    password="test",
    username="test",
)


@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


class TestInsert:
    data = {
        "name": "SurrealDB",
        "founded": "2021-09-10",
        "founders": ["tobie", "jaime"],
        "tags": ["big data", "database"],
    }

    @pytest.mark.asyncio
    async def test_insert(self):
        """Test the functionality of INSERT.

        Create an entry in the database.
        """
        insert_query = Query(config=config)
        table_name = "company"
        insert_query.insert(table_name, values=self.data)
        res = await insert_query.execute()
        res = res[0]["result"]
        assert res[0]["id"].split(":")[0] == table_name.split(" ")[0]
        assert res[0]["name"] == self.data["name"]
        assert res[0]["founded"] == "2021-09-10T00:00:00Z"
        assert res[0]["name"] == self.data["name"]


class TestInsertSQL:
    table_name = "person"
    data = tuple(["John", "SurrealDB", "2021-09-10"])
    SQL = "INSERT INTO company (name, founded) VALUES ('SurrealDB', '2021-09-10');"

    @pytest.mark.asyncio
    async def test_insert_sql(self):
        """Test the functionality of INSERT.

        Create an entry in the database.
        """
        insert_query = Query(config=config)
        table_name = f"{self.table_name} (name, company, founded)"
        insert_query.insert(table_name, values=self.data)
        res = await insert_query.execute()
        res = res[0]["result"]
        assert res[0]["company"] == "SurrealDB"
        assert res[0]["founded"] == "2021-09-10T00:00:00Z"
        assert res[0]["name"] == "John"

    @pytest.mark.asyncio
    @pytest.mark.dependency(on=["test_insert_sql"])
    async def test_select(self):
        """Test the functionality of INSERT by looking in the database."""
        query = Query(config=config)
        query.select("*").from_(self.table_name)
        res = await query.execute()
        res = res[0]["result"]
        assert res[0]["company"] == self.data[1]
        assert res[0]["founded"] == "2021-09-10T00:00:00Z"
        assert res[0]["name"] == self.data[0]


class TestInsertValue:
    table = "company"
    table_name = f"{table} (name, founded)"
    data = tuple(["SurrealDB", "2021-09-10"])

    @pytest.mark.asyncio
    async def test_insert_value(self):
        """Test the functionality of INSERT.

        Create an entry in the database.
        """
        insert_query = Query(config=config)
        insert_query.insert(self.table_name, values=self.data)
        res = await insert_query.execute()
        res = res[0]["result"]
        assert res[0]["name"] == "SurrealDB"
        assert res[0]["founded"] == "2021-09-10T00:00:00Z"

    @pytest.mark.asyncio
    @pytest.mark.dependency(on=["test_insert_value"])
    async def test_select2(self):
        """Test the functionality of INSERT by looking in the database."""
        query = Query(config=config)
        query.select("*").from_(self.table)
        res = await query.execute()
        res = res[0]["result"]
        assert res[0]["name"] == "SurrealDB"
        assert res[0]["founded"] == "2021-09-10T00:00:00Z"
