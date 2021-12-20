#!/usr/bin/env python

import datetime
# import click
import click_datetime
import collections
import peewee

__all__ = [f"psql_types_convert", f"psql_types_to_random"]

psql_types_convert_value = collections.namedtuple(f"psql_types_convert_value", [f"type", f"default"])

psql_types_convert: dict[str, psql_types_convert_value] = {
	f"character varying": psql_types_convert_value(str, lambda: None),
	f"varchar": psql_types_convert_value(str, lambda: None),
	f"bigint": psql_types_convert_value(int, lambda: None),
	f"int": psql_types_convert_value(int, lambda: None),
	f"integer": psql_types_convert_value(int, lambda: None),
	f"money": psql_types_convert_value(float, lambda: None),
	f"timestamp with time zone": psql_types_convert_value(click_datetime.Datetime(format="%Y-%m-%d"), lambda: datetime.datetime.now()),  # default=datetime.now(),%H:%M:%S
	f"timestamp without time zone": psql_types_convert_value(click_datetime.Datetime(format="%Y-%m-%d"), lambda: datetime.datetime.now()),
	f"timestampz": psql_types_convert_value(click_datetime.Datetime(format="%Y-%m-%d"), lambda: datetime.datetime.now()),
	f"timestamp": psql_types_convert_value(click_datetime.Datetime(format="%Y-%m-%d"), lambda: datetime.datetime.now()),
	f"boolean": psql_types_convert_value(bool, lambda: None),

	f"CharField": psql_types_convert_value(str, lambda: None),
	f"AutoField": psql_types_convert_value(int, lambda: None),
	f"DecimalField": psql_types_convert_value(int, lambda: None),
	f"DateTimeField": psql_types_convert_value(click_datetime.Datetime(format="%Y-%m-%d"), lambda: datetime.datetime.now()),

	peewee.ForeignKeyField: psql_types_convert_value(int, lambda: None),
	peewee.CharField: psql_types_convert_value(str, lambda: None),
	peewee.AutoField: psql_types_convert_value(int, lambda: None),
}

psql_types_to_random: dict[str] = {
	f"character varying": lambda x: f"""substr(characters, (random() * length(characters) + 1)::integer, 10)""",
	f"bigint": lambda x: f"""trunc(random() * 100)::int""",
	f"int": lambda x: f"""trunc(random() * 100)::int""",
	f"integer": lambda x: f"""trunc(random() * 100)::int""",
	f"numeric": lambda x: f"""trunc(random() * 100)::int""",
	f"money": lambda x: f"""trunc(random() * 100)::int""",
	f"timestamp with time zone": lambda x: f"""timestamp '2021-01-01' + random() * (timestamp '2021-11-11' - timestamp '2021-01-01')""",
	f"timestamp without time zone": lambda x: f"""timestamp '2021-01-01' + random() * (timestamp '2021-11-11' - timestamp '2021-01-01')""",
	f"boolean": lambda x: f"""round(random()),""",
}


def _test():
	pass


if __name__ == "__main__":
	_test()
