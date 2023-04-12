## Config Module

The `Config` class is used to configure the connection the database. It uses the `SurrealHTTP` and requires the following arguments:

- `url` : URL of the database
- `namespace` : The namespace of the database
- `database` : The name of the database
- `username` : The access username
- `password` : The access password
- `client` : an `SurrealHTTP` client configured beforehand
- `from_env`: if it set to `True` then it expects a `.db_conf` file where all the previous arguments are defined

## Query Module

The Query module aims to replace the standard SurrealQL and make it more Python friendly. Internally it constructs a SurrealQL string from method chaining and sends the query to the database.

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

```
query.select("*").from_("person")
```

- Execution

To execute the query run `res = await query.execute()`, where `res` is the result of the query.
