import asyncio

import pytest
from faker import Faker
from sirqle.query import Config, Query

fake = Faker()


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
        "name": fake.company(),
        "founded": fake.date(),
        "founders": [fake.name(), fake.name()],
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
        assert res[0]["id"].split(":")[0] == table_name.split(" ")[0]
        assert res[0]["name"] == self.data["name"]
        assert res[0]["founded"] == self.data["founded"]
        assert res[0]["name"] == self.data["name"]


class TestInsertSQL:
    table_name = "person"
    data = tuple([fake.name(), fake.company(), fake.date()])
    SQL = "INSERT INTO company (name, founded) VALUES ('Company 2', '2021-09-10');"

    @pytest.mark.asyncio
    async def test_insert_sql(self):
        """Test the functionality of INSERT.

        Create an entry in the database.
        """
        insert_query = Query(config=config)
        table_name = f"{self.table_name} (name, company, founded)"
        insert_query.insert(table_name, values=self.data)
        res = await insert_query.execute()
        self.id = res[0]["id"]
        assert res[0]["name"] == self.data[0]
        assert res[0]["company"] == self.data[1]
        assert res[0]["founded"] == self.data[2]

    @pytest.mark.asyncio
    @pytest.mark.dependency(on=["test_insert_sql"])
    async def test_select(self):
        """Test the functionality of INSERT by looking in the database."""
        query = Query(config=config)
        query.select().from_(self.table_name)
        res = await query.execute()
        assert res[0]["name"] == self.data[0]
        assert res[0]["company"] == self.data[1]
        assert res[0]["founded"] == self.data[2]


class TestInsertValue:
    table = "company"
    table_name = f"{table} (name, founded)"
    data = tuple([fake.company(), fake.date()])

    @pytest.mark.asyncio
    async def test_insert_value(self):
        """Test the functionality of INSERT.

        Create an entry in the database.
        """
        insert_query = Query(config=config)
        insert_query.insert(self.table_name, values=self.data)
        res = await insert_query.execute()
        assert res[0]["name"] == self.data[0]
        assert res[0]["founded"] == self.data[1]

    @pytest.mark.asyncio
    @pytest.mark.dependency(on=["test_insert_value"])
    async def test_select(self):
        """Test the functionality of INSERT by looking in the database."""
        query = Query(config=config)
        query.select("*").from_(self.table)
        res = await query.execute()
        assert res[0]["name"] == self.data[0]
        assert res[0]["founded"] == self.data[1]


class TestCreate:
    data = {
        "name": fake.name(),
        "company": fake.company(),
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
        await create_query.execute()

    @pytest.mark.asyncio
    @pytest.mark.dependency(on=["test_create"])
    async def test_select(self):
        """Test the functionality of CREATE by looking in the database."""
        query = Query(config=config)
        query.select(list(self.data.keys())).from_(self.table_name)
        res = await query.execute()
        assert res[0] == self.data
