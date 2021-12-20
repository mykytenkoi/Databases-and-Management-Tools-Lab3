#!/usr/bin/env python

import re
import Lab.utils
import collections
import psycopg2
import datetime
import psycopg2.extensions
import psycopg2.sql
import Lab.utils.psql_types
import types
from . import DynamicSearch

__all__ = [f"SchemaTable", f"SchemaTableORM", f"Schema"]


class SchemaTable(object):  # peewee.Model
	def __init__(self, schema=None, table=None):
		super().__init__()

		if table is None:
			table = type(self).__name__

		self.schema = schema
		self.table = table

		self.primary_key_name = f"id"

	def __str__(self):
		return f'"{self.table}"' if self.schema is None else f'"{self.schema}"."{self.table}"'

	def __hash__(self):
		return hash(str(self))

	def columns(self):
		# sql = f"""
		# 	SELECT column_name, data_type
		# 	FROM information_schema.columns
		# 	WHERE table_name = '{self.table}';
		# """

		sql = f"""
			SELECT
				tb.table_schema, tb.table_name, tb.column_name, tb.data_type, tb.is_nullable,
				fx.constraint_name, fx.references_schema, fx.references_table, fx.references_field
			FROM information_schema.columns tb
			LEFT JOIN (
				SELECT
					tc.constraint_schema,
					tc.table_name,
					kcu.column_name,
					tc.constraint_name,
					tc.constraint_type,
					rc.update_rule AS on_update,
					rc.delete_rule AS on_delete,
					ccu.constraint_schema AS references_schema,
					ccu.table_name AS references_table,
					ccu.column_name AS references_field
				FROM information_schema.table_constraints tc
				LEFT JOIN information_schema.key_column_usage kcu
					ON tc.constraint_catalog = kcu.constraint_catalog
					AND tc.constraint_schema = kcu.constraint_schema
					AND tc.constraint_name = kcu.constraint_name
				LEFT JOIN information_schema.referential_constraints rc
					ON tc.constraint_catalog = rc.constraint_catalog
					AND tc.constraint_schema = rc.constraint_schema
					AND tc.constraint_name = rc.constraint_name
				LEFT JOIN information_schema.constraint_column_usage ccu
					ON rc.unique_constraint_catalog = ccu.constraint_catalog
					AND rc.unique_constraint_schema = ccu.constraint_schema
					AND rc.unique_constraint_name = ccu.constraint_name
				WHERE tc.constraint_schema NOT ILIKE 'pg_%' AND tc.constraint_schema NOT ILIKE 'inform%' AND tc.constraint_type IN ('PRIMARY KEY', 'FOREIGN KEY')) fx
				ON fx.constraint_schema = tb.table_schema AND fx.table_name = tb.table_name AND fx.column_name = tb.column_name
			WHERE tb.table_schema = '{self.schema}' AND tb.table_name = '{self.table}'
			ORDER BY tb.ordinal_position;
		"""
		# row_type(table_schema='Lab', table_name='Users', column_name='id', data_type='bigint', is_nullable='NO', constraint_name='Users_pkey', references_schema=None, references_table=None, references_field=None),
		with self.schema.dbconn.cursor() as dbcursor:
			dbcursor.execute(sql)
			row_type = collections.namedtuple("row_type", (a[0] for a in dbcursor.description))
			result = tuple(row_type(*a) for a in dbcursor.fetchall())
			# result = {a: b for a, b in dbcursor.fetchall() if a not in [f"{self.primary_key_name}"]}
		return result

	def describe(self):
		print(f"{self} describe")
		sql = f"""
			SELECT table_name, column_name, data_type, character_maximum_length
			FROM information_schema.columns
			WHERE table_name = '{self.table}';
		"""
		return self.schema.showData(sql=sql)

	def addData(self, data: dict[collections.namedtuple] = None):
		if data is None:
			return Lab.utils.menuInput(self.addData, [a for a in self.columns() if a.column_name not in [f"{self.primary_key_name}"]])

		columns, values = zip(*{a.column_name: b for a, b in data.items()}.items())

		sql = f"""
			INSERT INTO {self} (%s) VALUES %s;
		"""

		with self.schema.dbconn.cursor() as dbcursor:
			try:
				dbcursor.execute(sql, (psycopg2.extensions.AsIs(", ".join(map(lambda x: f'"{x}"', columns))), values))
				self.schema.dbconn.commit()
			except Exception as e:
				self.schema.dbconn.rollback()
				print(f"Something went wrong: {e}")
				# raise e
			else:
				print(f"{dbcursor.rowcount} rows added")

	def editData(self, data: dict[collections.namedtuple] = None):
		if data is None:
			return Lab.utils.menuInput(self.editData, [a for a in self.columns() if a.column_name not in []])

		tmp = next(a for a in data if a.column_name in [f"{self.primary_key_name}"])
		rowid = data[tmp]
		del data[tmp]

		columns, values = zip(*{a.column_name: b for a, b in data.items()}.items())

		sql = f"""UPDATE {self} SET {", ".join(f'"{a}" = %s' for a in columns)} WHERE "{self.primary_key_name}" = {rowid};"""

		with self.schema.dbconn.cursor() as dbcursor:
			try:
				dbcursor.execute(sql, values)
				self.schema.dbconn.commit()
			except Exception as e:
				self.schema.dbconn.rollback()
				print(f"Something went wrong: {e}")
			else:
				print(f"{dbcursor.rowcount} rows changed")

	def removeData(self, rowid=None):
		# rowid = click.prompt(f"{self.primary_key_name}", type=int)
		if rowid is None:
			return Lab.utils.menuInput(self.removeData, [a for a in self.columns() if a.column_name in [f"{self.primary_key_name}"]])

		if isinstance(rowid, dict):
			rowid = rowid[next(a for a in rowid if a.column_name in [f"{self.primary_key_name}"])]

		sql = f"""DELETE FROM {self} WHERE "{self.primary_key_name}" = {rowid};"""

		with self.schema.dbconn.cursor() as dbcursor:
			try:
				dbcursor.execute(sql)
				self.schema.dbconn.commit()
			except Exception as e:
				self.schema.dbconn.rollback()
				print(f"Something went wrong: {e}")
			else:
				print(f"{dbcursor.rowcount} rows deleted")

	def showData(self, sql=None):
		# print(showDataCreator)
		if sql is None:
			sql = f"""SELECT * FROM {self};"""

		return self.schema.showData(sql=sql)

	def dynamicsearch(self):
		raise NotImplementedError

	def randomFill(self, instances: int = None, str_len: int = 10, sql_replace: str = None):

		if sql_replace:
			pass
		else:
			if instances is None:
				return Lab.utils.menuInput(self.randomFill, [collections.namedtuple("instances", ["column_name", "data_type", "default"])("instances", "int", lambda: 100)])
			
			if isinstance(instances, dict):
				instances = instances[next(a for a in instances if a.column_name in ["instances"])]

			columns = tuple(a for a in self.columns() if a.column_name not in [f"{self.primary_key_name}"])

			def psql_foreign_key_random(x):
				result = f"""
					(SELECT "{x.references_field}" FROM "{x.references_schema}"."{x.references_table}" ORDER BY random()*q LIMIT 1)
				"""
				return result

			sql = ",\n"
			sql = f"""
				INSERT INTO {self}({", ".join(map(lambda x: f'"{x.column_name}"', columns))})
				SELECT
					{sql.join(map(lambda x: Lab.utils.psql_types.psql_types_to_random[x.data_type](x) if x.references_field is None else psql_foreign_key_random(x), columns))}
				FROM
					(VALUES('qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM')) as symbols(characters),
					generate_series(1, {instances}) as q;
			"""

		sql = sql_replace or sql
		# with self.schema.dbconn:
		with self.schema.dbconn.cursor() as dbcursor:
			try:
				# print(sql)
				t1 = datetime.datetime.now()
				dbcursor.execute(sql)
				t2 = datetime.datetime.now()
				self.schema.dbconn.commit()
			except Exception as e:
				self.schema.dbconn.rollback()
				print(f"Something went wrong: {e}")
			else:
				print(f"{self} {dbcursor.rowcount} rows added, execution time: {t2 - t1}")

	@property
	def promt(self):
		return f"{self} table interface:"

	@property
	def __lab_console_interface__(self):
		result = Lab.utils.LabConsoleInterface({
			f"describe": self.describe,
			f"show data": self.showData,
			f"add data": self.addData,
			f"edit data": self.editData,
			f"remove data": self.removeData,
			f"random fill": self.randomFill,
			f"return": lambda: Lab.utils.menuReturn(f"User menu return"),
		}, promt=self.promt)
		return result


class SchemaTableORM(SchemaTable):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.ORM = None

	def removeData(self, rowid=None):
		if rowid is None:
			return Lab.utils.menuInput(self.removeData, [a for a in self.columns() if a.column_name in [f"{self.primary_key_name}"]])

		if isinstance(rowid, dict):
			rowid = rowid[next(a for a in rowid if a.column_name in [f"{self.primary_key_name}"])]

		rowcount = self.ORM.delete_by_id(rowid)
		print(f"{rowcount} rows deleted")

	def addData(self, data: dict[collections.namedtuple] = None):
		if data is None:
			return Lab.utils.menuInput(self.addData, [collections.namedtuple("instances", ["column_name", "data_type", "default"])(a, type(b), lambda: None) for a, b in self.ORM._meta.fields.items() if a not in [f"{self.primary_key_name}"]])

		data = {a.column_name: b for a, b in data.items()}

		with self.schema.dbconn:
			rowcount = self.ORM.create(**data)
			print(f"{rowcount} rows added")

	def editData(self, data: dict[collections.namedtuple] = None):
		if data is None:
			return Lab.utils.menuInput(self.editData, [collections.namedtuple("instances", ["column_name", "data_type", "default"])(a, type(b), lambda: None) for a, b in self.ORM._meta.fields.items() if a not in []])

		tmp = next(a for a in data if a.column_name in [f"{self.primary_key_name}"])
		rowid = data[tmp]
		del data[tmp]

		data = {a.column_name: b for a, b in data.items()}

		with self.schema.dbconn:
			rowcount = self.ORM.update(**data).where(self.ORM.id == rowid).execute()  # setattr(self.ORM, a, b) getattr(self.ORM, a)
			print(f"{rowcount} rows changed")

	def showData(self):
		# q = self.ORM._meta.fields[f"Name"]
		# print(type(q), dir(q))
		# result = Lab.utils.TablePrint()
		# # print(type(self.ORM.select()))

		# t1 = datetime.datetime.now()
		# q = self.ORM.select()
		# t2 = datetime.datetime.now()
		# result.executiontime = t2 - t1
		# result.table = Lab.utils.ModelSelectTable(q, self.ORM._meta.fields.keys())
		# result.rowcount = len(result.table) - 1
		# return result
		return self.schema.showData(sql=self.ORM.select())


class SchemaTables(object):
	def __init__(self, schema, *tables):
		super().__init__()
		self.schema = schema
		self._tables = {str(a): (SchemaTable(self.schema, a) if isinstance(a, str) else a) for a in tables}
		# self._iter = 0

	# @property
	# def tables(self):
	# 	return self._tables.keys()

	def __str__(self):
		return f"{self.schema}({type(self).__name__}({set(self._tables.keys())}))"

	def __getattr__(self, name):
		try:
			if name in [f"_tables"]:
				raise KeyError
			return self._tables[name]
		except KeyError as e:
			try:
				return super().__getattribute__(name)
			except KeyError as e:
				raise AttributeError(f"{name} is not known table")

	def __setattr__(self, key, value):
		if re.match(r"^[A-Z]$", key[0]):
			# print(f"sttr {key} {value}")
			self._tables[key] = value
		else:
			super().__setattr__(key, value)

	def __getitem__(self, key: str):
		try:
			return self._tables[key]
		except KeyError as e:
			raise KeyError(f"{key} is not known table")

	def __setitem__(self, key, value):
		self._tables[key] = value

	def __iter__(self):
		# self._iter = iter(self._tables.values())
		return iter(self._tables.values())

	# def __next__(self):
		# try:
		# 	result = tuple(self._tables.values())[self._iter]  # may be optimized
		# except IndexError as e:
		# 	self._iter = 0
		# 	raise StopIteration
		# self._iter += 1
		# return result

	# def __getitem__(self, key)


class Schema(object):
	def __init__(self, dbconn, name=None):
		super().__init__()
		if name is None:
			name = type(self).__name__
		self.dbconn = dbconn
		self.name: str = name
		self._tables: tuple = tuple()
		self._dynamicsearch: dict[str, DynamicSearchBase] = dict()
		self.alias = types.SimpleNamespace()
		self.refresh_tables()
		self.reoverride()

	def __str__(self):
		return self.name

	def __getitem__(self, key):
		return self.tables[key]

	def __iter__(self):
		return iter(self._tables)

	def showData(self, sql, column_names_override=tuple()):
		sql = f"{sql}"
		with self.dbconn.cursor() as dbcursor:
			try:
				# print(sql)
				t1 = datetime.datetime.now()
				dbcursor.execute(sql)
				t2 = datetime.datetime.now()
			except Exception as e:
				self.dbconn.rollback()
				print(f"Something went wrong: {e}")
			else:
				q = Lab.utils.TablePrint()
				q.rowcount = dbcursor.rowcount
				q.table = Lab.utils.fetchall_table(dbcursor, column_names_override)
				q.executiontime = t2 - t1

				return q

	def reoverride(sef):
		pass

	def refresh_tables(self):
		# self._tables: tuple = tuple()
		# sql = f"""
		# 	SELECT table_name
		# 	FROM information_schema.tables
		# 	WHERE table_schema = '{self.name}';
		# """
		# with self.dbconn.cursor() as dbcursor:
		# 	dbcursor.execute(sql)
		# 	q = (*(a[0] for a in dbcursor.fetchall()),)
		# 	self._tables = SchemaTables(self, *q)  # collections.namedtuple("Tables", q)(*map(SchemaTables, q))
		# pprint.pprint(self._tables)
		self._tables = SchemaTables(self)
		self.reoverride()
		return self._tables

	def dump_sql(self):
		pass

	def reinit(self):
		raise NotImplementedError(f"Need to override")

	def randomFill(self):
		raise NotImplementedError(f"Need to override")

	@property
	def tables(self):
		return self._tables

	@property
	def dynamicsearch(self):
		return self._dynamicsearch

	# def dynamicsearch(self):
	# 	raise NotImplementedError(f"Need to override")

	@property
	def promt(self):
		return f'Schema "{self}" interface'

	@property
	def __lab_console_interface__(self):
		result = Lab.utils.LabConsoleInterface({
			**{f'"{a.table}" table': (lambda a: lambda: a)(a) for a in self.tables},
			f'Schema "{self}" utils':
				lambda: Lab.utils.LabConsoleInterface({
					"reinit": self.reinit,
					"random fill": self.randomFill,
					# "dump sql": self.dump_sql,
					"return": lambda: Lab.utils.menuReturn(f"User menu return"),
				}, promt=f'Schema "{self}" utils'),
			f"Dynamic search": lambda: Lab.utils.LabConsoleInterface({
				**{a: (lambda x: lambda: x)(b) for a, b in self.dynamicsearch.items()},
				"return": lambda: Lab.utils.menuReturn(f"User menu return"),
				}, promt=f"""Schema "{self}" dynamic search interface""")
				# self.dynamicsearch,
		}, promt=self.promt)

		return result



def _test():
	pass


if __name__ == "__main__":
	_test()
