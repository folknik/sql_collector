"""
Based on https://stackoverflow.com/questions/56070157/creating-a-function-to-automate-sql-joins
"""

import json
from collections import deque

from tools import read_yml_file


def bfs(nodes, children, start):
    parent = {}
    q = deque([start])

    while q:
        v = q.popleft()
        for w in children[v]:
            if w not in parent:
                parent[w] = v
                q.append(w)

    return parent


def join_sql(schema: dict, main_table: str, *tables) -> str:
    # for each table, which tables does it connect to?
    children_map = {table: set() for table in schema}
    for child, properties in schema.items():
        parents = properties['fk']
        for parent in parents:
            children_map[parent].add(child)

    # What are all the tables in consideration?
    nodes = set(schema.keys())

    # get a tree of parent tables via breadth-first search.
    parent_tree = bfs(nodes, children_map, main_table)

    # Create a topological ordering on the graph;
    # order so that parent is joined before child.
    join_order = []
    used = {main_table}

    def add_to_join_order(t):
        if t in used or t is None:
            return
        parent = parent_tree.get(t, None)
        add_to_join_order(parent)
        join_order.append(t)
        used.add(t)

    for table in tables:
        add_to_join_order(table)

    parent_table_schema = schema[main_table]['schema']
    parent_table_alias = schema[main_table]['alias']

    columns = []
    for column in schema[main_table]['columns']:
        columns.append(
            f'    {parent_table_alias}."{column}"'
        )

    filters = []
    parent_filter = schema[main_table]['filter']
    if len(parent_filter) > 0:
        if parent_filter['type'] == 'BETWEEN':
            col = f"{parent_table_alias}.\"{parent_filter['column']}\""
            filters.append(
                col + " BETWEEN '{start}' AND '{end}'"
            )

    lines = [f'FROM {parent_table_schema}."{main_table}" AS {parent_table_alias}']
    for fk_table in join_order:
        parent_table = parent_tree[fk_table]
        parent_col = schema[parent_table]['pk']
        fk_table_schema = schema[fk_table]['schema']
        fk_table_alias = schema[fk_table]['alias']
        fk_col = schema[fk_table]['pk']
        lines.append(
            f'INNER JOIN {fk_table_schema}."{fk_table}" AS {fk_table_alias} ON {fk_table_alias}.{fk_col} = {parent_table_alias}.{parent_col}'
        )

        for column in schema[fk_table]['columns']:
            columns.append(
                f'    {fk_table_alias}."{column}"'
            )

        fk_filter = schema[fk_table]['filter']
        if len(fk_filter) > 0:
            if fk_filter['type'] == 'BETWEEN':
                col = f"{fk_table_alias}.\"{fk_filter['column']}\""
                filters.append(
                    col + " BETWEEN '{start}' AND '{end}'"
                )

    lines.insert(
        0,
        'SELECT\n' + ',\n'.join(columns)
    )

    lines.append('WHERE ' + ' AND '.join(filters))

    return "\n".join(lines)


def main(config: str) -> None:
    schema = read_yml_file(file_path=config)
    print(json.dumps(schema, indent=4))
    query = join_sql(schema, 'Clients', 'BillingContracts')
    print(query)


if __name__ == "__main__":
    main('./resources/config.yml')