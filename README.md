# Sirqle

Surreal DB with Python wrapper for [surrealdb.py](https://github.com/surrealdb/surrealdb.py) which makes it easy to write SurrealQL queries in Python.

Install with:

```sh
pip install sirqle
```

Usage:

```python

from sirqle.query import Config, Query

config = Config(
        url = "localhost:8000",
        namespace = "test",
        database = "test",
        username = "test",
        password = "test",
)
my_query = Query(config=config)

table_name = "person"
cont = {
    "name": "Tobie",
    "company": "SurrealDB",
    "skills": ["Rust", "Go", "JavaScript"],
}
my_query.create(table_name).content(cont)
response = await my_query.execute()

# the result

response = [{'company': 'SurrealDB', 'id': 'person:it2e579rij23zu0iswk4', 'name': 'Tobie', 'skills': ['Rust', 'Go', 'JavaScript']}]
```

## Config Module

The `Config` class is used to configure the connection the database. It uses the `SurrealHTTP` client and requires the following arguments depending on the desired method:

> 1. Manually enter the parameters

- `url` : URL of the database
- `namespace` : The namespace of the database
- `database` : The name of the database
- `username` : The access username
- `password` : The access password

> 2. Pass a previous defined client

- `client` : an `SurrealHTTP` client from `surrealdb.py`

> 3. Load the parameters from a file

- `env_file`: the name of the env file. Defaults to `.db_conf`.

## Query Module

The Query module aims to extend the standard SurrealQL and make it more Python friendly. Internally it constructs a SurrealQL string from method chaining and sends the query to the database.

### Initialize the query

```python
query = Query(config)
```

### Create examples

Create a new entry:

```sql
CREATE person CONTENT {
name: 'Tobie',
company: 'SurrealDB',
skills: ['Rust', 'Go', 'JavaScript']
};
```

becomes

```python
table_name = "person"
cont = {
    "name": "Tobie",
    "company": "SurrealDB",
    "skills": ["Rust", "Go", "JavaScript"],
}
create_query.create(table_name).content(cont)
```

### Insert example

```sql
INSERT INTO person (name, company, founded) VALUES ('John', 'SurrealDB', '2021-09-10');
```

becomes

```python
table_name = "person (name, company, founded)"
data = tuple(["John", "SurrealDB", "2021-09-10"])
insert_query.insert(table_name, values=data)
```

### Select example

```sql
SELECT * FROM person;
```

becomes

```python
query.select("*").from_("person")
```

> **Execution**

To execute the query run `res = await query.execute()`, where `res` is the result of the query.

### Custom query example

If you need something more complex than the basic operations, you can directly pass an SurrealQL query as a string:

> This query creates a temporary entry in the table `Topic` where we hash the values of `topic_label` and `topic_source`, returns the hash value and then delete the table.

```python
table_name = "Topic"
topic_label = "SurrealDB is awesome"
topic_source = "My personal knowledge"
my_query.custom( f"create {table_name} content"
                + f" {{words: {topic_label}, source: {topic_source}}}"
                + f" return crypto::md5(string::concat($this.words, $this.source));"
                + f" delete from {table_name};")
response = await my_query.execute()
response = {"crypto::md5": "8f23a9630e18d525946740e5498798be"}
```
