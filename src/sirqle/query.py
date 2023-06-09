from __future__ import annotations

import os
from typing import List, Optional, Tuple
from urllib.parse import urlparse
from warnings import warn

from dotenv import dotenv_values
from surrealdb.http import SurrealHTTP
from surrealdb.ws import ConnectionState, Surreal

PARAMS = ["URL", "NAMESPACE", "USERNAME", "PASSWORD", "DATABASE"]


CLIENT = {
    "ws": Surreal,
    "wss": Surreal,
    "http": SurrealHTTP,
    "https": SurrealHTTP,
}


class Config:
    def __init__(
        self,
        env_file: str = ".db_conf",
        client: Optional[SurrealHTTP | Surreal] = None,
        url: Optional[str] = None,
        namespace: Optional[str] = None,
        database: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None:
        """Generate a Config class is used to configure the connection the database.

        It uses the `SurrealHTTP` client from the `surrealdb` library

        Args:
            env_file: the name of an env file
            client: a predefined Surreal client
            url: the URL to the database
            namespace: the namespace in the database
            database: the name of the database
            username: the username used for authentication
            password: the password used for authentication
        """
        if client:
            self.client = client
        elif os.path.isfile(env_file):
            conf = dotenv_values(env_file)
            if set(PARAMS).issubset(set(conf.keys())):
                scheme = str(urlparse(conf["URL"]).scheme)
                self.client = CLIENT[scheme](
                    **{param.lower(): conf[param] for param in PARAMS}
                )
        elif username and database and password and namespace and url:
            scheme = str(urlparse(url).scheme)
            self.client = CLIENT[scheme](
                url,
                namespace=namespace,
                database=database,
                username=username,
                password=password,
            )
        elif url:
            scheme = str(urlparse(url).scheme)
            if scheme in ["wss", "ws"]:
                self.client = CLIENT[scheme](url=url)

    async def signup(self, user: str, password: str) -> str:
        if isinstance(self.client, Surreal):
            if self.client.client_state != ConnectionState.CONNECTED:
                await self.client.connect()
        return await self.client.signup({"user": user, "pass": password})

    async def signin(self, user: str, password: str) -> str:
        if isinstance(self.client, Surreal):
            if self.client.client_state != ConnectionState.CONNECTED:
                await self.client.connect()
        return await self.client.signin({"user": user, "pass": password})


class Query:
    def __init__(self, config: Config | None = None):
        """Create a `Query` class

        The Query module aims to replace the standard SurrealQL and make it more Python
            friendly. Internally it constructs a SurrealQL string from method chaining
            and sends the query to the database.

        Args:
            config: a `Config` object
        """
        self.query = ""
        self.last_query = ""
        # TODO Process config here rather than having to instantiate another
        if config:
            self.client = config.client

    def _parse_args(self, args: str | list | dict | tuple | Query, quote=True) -> str:
        if isinstance(args, str):
            if quote and ":" not in args:
                return f"'{args}'"
            return args
        elif isinstance(args, list):
            if quote:
                return "[" + ", ".join([self._parse_args(arg) for arg in args]) + "]"
            else:
                return ", ".join(args)
        elif isinstance(args, dict):
            return (
                "{"
                + "".join(
                    [
                        f"\n{key}: {self._parse_args(value)}, "
                        for key, value in args.items()
                    ]
                )
                + "\n}"
            )
        elif isinstance(args, tuple):
            return (
                "(" + ", ".join([f"{self._parse_args(value)}" for value in args]) + ")"
            )

        elif isinstance(args, Query):
            return f"({args[:-1]})"
        elif isinstance(args, int):
            return args

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
        Args:

            args: a table or a list of tables

        Returns:
            Query: returns the same `Query` object
        """
        self.query = " SELECT "
        self.query += self._parse_args(args, quote=False)
        return self

    def insert(
        self, args: str, values: Tuple[str] | List[Tuple[str]] | dict | str = ""
    ) -> Query:
        """INSERT statement.

        Args:
            args: arguments for the statement

        Returns:
            Query: returns the same `Query` object
        """
        self.query += "INSERT INTO "
        self.query += self._parse_args(args, quote=False) + " "
        if values:
            if isinstance(values, (str, tuple)):
                self.query += " VALUES "
                self.query += self._parse_args(values)
            elif isinstance(values, (list, dict)):
                self.query += self._parse_args(values)
            else:
                raise NotImplementedError()
        return self

    def create(self, args: str | list | dict | Query) -> Query:
        """CREATE statement.

        Args:
            args: arguments for the statement

        Returns:
            Query: returns the same `Query` object
        """
        self.query += " CREATE "
        self.query += self._parse_args(args, quote=False)
        return self

    def update(self, args: str | list | dict | Query) -> Query:
        """UPDATE statement.

        Args:
            args: arguments for the statement

        Returns:
            Query: returns the same `Query` object
        """
        self.query += " UPDATE "
        self.query += self._parse_args(args, quote=False)
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
            self.query += self._parse_args(args)
        return self

    def delete(self, args: str | list | dict | Query) -> Query:
        """DELETE statement.

        Args:
            args: arguments for the statement

        Returns:
            Query: returns the same `Query` object
        """
        self.query += " DELETE "
        self.query += self._parse_args(args, quote=False)
        return self

    def define(self, args: str | list | dict | Query) -> Query:
        """DEFINE statement.

        Args:
            args: arguments for the statement

        Returns:
            Query: returns the same `Query` object
        """
        self.query += " DEFINE "
        self.query += self._parse_args(args, quote=False)
        return self

    def from_(self, args: str | list | dict | Query) -> Query:
        """FROM statement.

        Args:
            args: arguments for the statement

        Returns:
            Query: returns the same `Query` object
        """
        self.query += " FROM "
        self.query += self._parse_args(args, quote=False)
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
            self.query += self._parse_args(args, quote=False)
        else:
            warn(
                "No arguments for RETURN statement. RETURN statement not \
                added to the query."
            )
        return self

    def return_(self, args: str | list | dict | Query | None) -> Query:
        """RETURN statement.

        Args:
            args: arguments for the statement

        Returns:
            Query: returns the same `Query` object
        """
        if args:
            self.query += " RETURN "
            self.query += self._parse_args(args, quote=False)
        else:
            warn(
                "No arguments for RETURN statement. RETURN statement not \
                added to the query."
            )
        return self

    def content(self, args: str | list | dict | Query) -> Query:
        """CONTENT statement.

        Args:
            args: arguments for the statement

        Returns:
            Query: returns the same `Query` object
        """
        self.query += " CONTENT "
        self.query += self._parse_args(args)
        return self

    def _end(self):
        self.query = self.query.strip()
        if self.query[-1] != ";":
            self.query += ";"

    async def _execute_query(self):
        self._end()
        if isinstance(self.client, Surreal):
            if self.client.client_state != ConnectionState.CONNECTED:
                await self.client.connect()
        res = await self.client.query(self.query)
        self.last_query = self.query
        self.query = ""
        return res

    async def execute(self):
        """Execute the query.

        Send the query to the databse and get the answert.

        """
        if self.client is None:
            raise Exception("No client provided!")
        res = await self._execute_query()
        return res

    async def use(self, ns: str, db: str) -> None:
        if isinstance(self.client, Surreal):
            await self.client.use(namespace=ns, database=db)
        elif isinstance(self.client, SurrealHTTP):
            self.client = SurrealHTTP(
                url=self.client._url,
                namespace=ns,
                database=db,
                username=self.client._username,
                password=self.client._password,
            )

    # HACK:
    def __repr__(self):
        self._end()
        return self.query

    def __getitem__(self, key):
        return self.query[key]
