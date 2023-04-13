import asyncio

import pytest

from sirqle.query import Config, Query

config = Config(env_file=".db_conf")


@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


class TestCreate:
    data = {
        "name": "Tobie",
        "company": "SurrealDB",
        "skills": ["Rust", "Go", "JavaScript"],
    }
    table_name = "person"

    @pytest.mark.asyncio
    async def test_create(self):
        """Test the functionality of CREATE.

        Create an entry in the database.
        """
        create_query = Query(config=config)
        create_query.create(self.table_name).content(self.data)
        res = await create_query.execute()
        res = res[0]["result"]

    @pytest.mark.asyncio
    @pytest.mark.dependency(on=["test_create"])
    async def test_select(self):
        """Test the functionality of CREATE by looking in the database."""
        query = Query(config=config)
        query.select(list(self.data.keys())).from_(self.table_name)
        res = await query.execute()
        res = res[0]["result"]
        assert res[0] == self.data
