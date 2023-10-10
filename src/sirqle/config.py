import os
from typing import Optional
from urllib.parse import urlparse

from dotenv import dotenv_values
from surrealdb.http import SurrealHTTP
from surrealdb.ws import Surreal

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
        else:
            url = os.environ.get("SURREAL_URL")
            namespace = os.environ.get("SURREAL_NS")
            username = os.environ.get("SURREAL_DB")
            username = os.environ.get("SURREAL_USER")
            password = os.environ.get("SURREAL_PASSWORD")
            scheme = str(urlparse(url).scheme)
            self.client = CLIENT[scheme](
                url,
                namespace=namespace,
                database=database,
                username=username,
                password=password,
            )
