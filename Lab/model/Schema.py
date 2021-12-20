#!/usr/bin/env python3

# import psycopg2
# import psycopg2.sql
# import psycopg2.extensions
import Lab.utils
import peewee


from . import DynamicSearch
from .AutoSchema import *


database_proxy = peewee.DatabaseProxy()


class Telecommunications_table(peewee.Model):
	class Meta(object):
		database = database_proxy
		schema = f"Telecommunications"


class Tariff(Telecommunications_table):
	Name = peewee.CharField(max_length=63, null=False)
	Price = peewee.DecimalField(null=False)
	Call_time = peewee.BigIntegerField(null=False)
	Trafic = peewee.BigIntegerField(null=False)
	SMS = peewee.BigIntegerField(null=False)


class User(Telecommunications_table):
	TariffID = peewee.ForeignKeyField(Tariff, backref="used_by")
	Name = peewee.CharField(max_length=63, null=False)
	Surname = peewee.CharField(max_length=63, null=False)
	Patronymic = peewee.CharField(max_length=63, null=False)
	Address = peewee.CharField(max_length=255, null=False)
	Call_time_left = peewee.BigIntegerField(null=False)
	Trafic_left = peewee.BigIntegerField(null=False)
	SMS_left = peewee.BigIntegerField(null=False)


class Call(Telecommunications_table):
	User_from = peewee.ForeignKeyField(User, backref="called_to")
	User_to = peewee.ForeignKeyField(User, backref="called_by")
	Name = peewee.CharField(max_length=127, null=False)
	Call_time = peewee.DateTimeField(null=False)
	Duration = peewee.BigIntegerField(null=False, default=0)

	# class Meta(object):
	# 	database = database_proxy
	# 	schema = f"Telecommunications"
	# 	# indexes = (
	# 	# 	((f"User_from", f"User_to"), True, ),
	# 	# )


class TariffTable(SchemaTableORM):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.ORM = Tariff


class UserTable(SchemaTableORM):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.ORM = User


class CallTable(SchemaTableORM):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.ORM = Call


class Telecommunications(Schema):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._dynamicsearch = {a.name: a for a in [DynamicSearch.UserDynamicSearch(self), DynamicSearch.CallDynamicSearch(self)]}
		database_proxy.initialize(self.dbconn)
		# self.reoverride()

	def reoverride(self):
		# print(f"reoverride")
		# Table override

		self.tables.Tariff = TariffTable(self, f"tariff")
		self.tables.User = UserTable(self, f"user")
		self.tables.Call = CallTable(self, f"call")

		self.alias.User_from = self.tables.User.ORM.alias()
		self.alias.User_to = self.tables.User.ORM.alias()

	def reinit(self):
		# sql = f"""
		# 	SELECT table_name FROM information_schema.tables
		# 	WHERE table_schema = '{self}';
		# """
		with self.dbconn.cursor() as dbcursor:
			# dbcursor.execute(sql)
			for a in self.refresh_tables():  # tuple(dbcursor.fetchall()):
				q = f"""DROP TABLE IF EXISTS {a} CASCADE;"""
				# print(q)
				dbcursor.execute(q)

		self.dbconn.create_tables([Tariff, User, Call])
		self.dbconn.commit()
		self.refresh_tables()
		# self.reoverride()

	def randomFill(self):
		self.tables.Tariff.randomFill(1_000)
		self.tables.User.randomFill(2_000)
		self.tables.Call.randomFill(10_000)


def _test():
	pass


if __name__ == "__main__":
	_test()
