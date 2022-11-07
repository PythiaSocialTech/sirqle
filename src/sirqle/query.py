from __future__ import annotations

import asyncio
from distutils.util import execute
from typing import List

from dotenv import dotenv_values
from surrealdb.clients.http import HTTPClient

# query.select(*).from(query.select().from()).where(jdsaf;)


class Config:
    def __init__(
        self,
        url: str = "",
        namespace: str = "",
        database: str = "",
        username: str = "",
        password: str = "",
        client: HTTPClient | None = None,
        from_env: bool = False,
    ) -> None:
        """Generate a Config class is used to configure the connection the database.

        It uses the `HTTPClient` from the `surrealdb` library

        Args:
            url: the URL to the database
            namespace: the namespace in the database
            database: the name of the database
            username: the username used for authentication
            password: the password used for authentication
            client: an `HTTPClient` configured beforehand
            from_env: if it's set to True, it will load an `.db_conf` file that has all the previous arguments set

        """
        if client:
            self.client = client
        elif from_env:
            conf = dotenv_values(".db_conf")
            try:
                self.client = HTTPClient(
                    url=conf["URL"],
                    namespace=conf["NAMESPACE"],
                    database=conf["DATABASE"],
                    username=conf["USERNAME"],
                    password=conf["PASSWORD"],
                )
            except Exception as e:
                print(type(e))
                print(e)
        else:
            try:
                self.client = HTTPClient(
                    url,
                    namespace=namespace,
                    database=database,
                    username=username,
                    password=password,
                )
            except Exception as e:
                print(type(e))
                print(e)


class Query:
    def __init__(self, config: Config | None = None):
        """Create a `Query` class

        The Query module aims to replace the standard SurrealQL and make it more Python friendly. Internally it constructs a SurrealQL string from method chaining and sends the query to the database.

        Args:
            config: a `Config` object
        """
        self.query = ""
        self.last_query = ""
        if (
            config
        ):  # TODO Process config here rather than having to instantiate another Config object
            self.client = config.client

    def _parse_args(self, args):
        if isinstance(args, str):
            self.query += args
        elif isinstance(args, list):
            for arg in args:
                self.query += arg + ","
            self.query = self.query[:-1]
        elif isinstance(args, dict):
            self.query += "{"
            for key, value in args.items():
                if not isinstance(value, str):
                    self.query += f"\n{key}: {value}, "
                else:
                    self.query += f"\n{key}: '{value}', "
            self.query = self.query[:-2]
            self.query += "\n}"
        elif isinstance(args, tuple):
            self.query += "("
            for value in args:
                if not isinstance(value, str):
                    self.query += f"{value}, "
                else:
                    self.query += f"'{value}', "
            self.query = self.query[:-2]
            self.query += ")"
        elif isinstance(args, Query):
            if args[-1] == ";":
                args = args[:-1]
            self.query += f"({args})"

    def custom(self, args: str) -> Query:
        """Create a simple query in SurrealQL.


        Args:
            args: a string containing a full and correct query

        Returns:
            Query: returns the same `Query` object
        """
        self.query += args
        return self

    def select(self, args: str | List[str]) -> Query:
        """SELECT statement.

        [TODO:description]

        Args:
            args: a table or a list of tables

        Returns:
            Query: returns the same `Query` object
        """
        self.query = " SELECT "
        self._parse_args(args)
        return self

    def from_(self, args: str | list | dict | Query) -> Query:
        """FROM statement.

        Args:
            args: arguments for the statement

        Returns:
            Query: returns the same `Query` object
        """
        self.query += " FROM "
        self._parse_args(args)
        return self

    def where(self, args: str | list | dict | Query) -> Query:
        """WHERE statement.

        Args:
            args: arguments for the statement

        Returns:
            Query: returns the same `Query` object
        """
        if args:
            self.query += " WHERE "
            self._parse_args(args)
        return self

    def use(self, args: str | list | dict | Query) -> Query:
        """USE statement.

        Args:
            args: arguments for the statement

        Returns:
            Query: returns the same `Query` object
        """
        self.query += " USE "
        self._parse_args(args)
        return self

    def return_(self, args: str | list | dict | Query) -> Query:
        """RETURN statement.

        Args:
            args: arguments for the statement

        Returns:
            Query: returns the same `Query` object
        """
        self.query += " RETURN "
        self._parse_args(args)
        return self

    def insert(
        self, args: str | list | dict | Query, values: tuple[str] | str = ""
    ) -> Query:
        """INSERT statement.

        Args:
            args: arguments for the statement

        Returns:
            Query: returns the same `Query` object
        """
        self.query += "INSERT INTO "
        if values:
            if isinstance(args, str):
                self.query += args
                self.query += " VALUES "
                self._parse_args(values)
            else:
                raise Exception(
                    f"Incorrect argument type, expected {type(str)} got {type(args)}"
                )
        else:
            self._parse_args(args)

        return self

    def delete(self, args: str | list | dict | Query) -> Query:
        """DELETE statement.

        Args:
            args: arguments for the statement

        Returns:
            Query: returns the same `Query` object
        """
        self.query += " DELETE "
        self._parse_args(args)
        return self

    def update(self, args: str | list | dict | Query) -> Query:
        """UPDATE statement.

        Args:
            args: arguments for the statement

        Returns:
            Query: returns the same `Query` object
        """
        self.query += " UPDATE "
        self._parse_args(args)
        return self

    def create(self, args: str | list | dict | Query) -> Query:
        """CREATE statement.

        Args:
            args: arguments for the statement

        Returns:
            Query: returns the same `Query` object
        """
        self.query += " CREATE "
        self._parse_args(args)
        return self

    def relate(
        self,
        node1: str,
        edge: str,
        node2: str,
        args: str | list | dict | Query | None = None,
    ) -> Query:
        """RELATE statement.

        Create a relation between two nodes.

        Args:
            node1: the source node
            edge: name of the relation
            node2: the destination node
            args: arguments for the statement

        Returns:
            Query: returns the same `Query` object
        """
        self.query += f" RELATE {node1}->{edge}->{node2}"
        if args:
            self.query += " CONTENT "
            self._parse_args(args)
        return self

    def content(self, args: str | list | dict | Query) -> Query:
        """CONTENT statement.

        Args:
            args: arguments for the statement

        Returns:
            Query: returns the same `Query` object
        """
        self.query += " CONTENT "
        self._parse_args(args)
        return self

    # NOTE: do we still need this?
    def __getitem__(self, key):
        return self.query[key]

    def _end(self):
        if self.query[0] == " ":
            self.query = self.query[1:]
        if self.query[-1] != ";":
            self.query += ";"

    async def _execute_query(self):
        self._end()
        res = await self.client.execute(self.query)
        self.last_query = self.query
        self.query = ""
        return res

    async def execute(self):
        """Execute the query.

        Send the query to the databse and get the answert.

        """
        if self.client == None:
            raise Exception("No client provided!")
        res = await self._execute_query()
        return res

    # HACK:
    def __repr__(self):
        self._end()
        return self.query
