#!/usr/bin/env python
import itertools
import pprint

from .dynamicsearch import *

__all__ = [
	f"UserDynamicSearch",
	f"CallDynamicSearch",
]


class UserDynamicSearch(DynamicSearchBaseORM):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.name: str = f"User"
		Tariff = self.schema.tables.Tariff.ORM
		User = self.schema.tables.User.ORM
		self.search: dict[self.SearchCriteriasORM[CompareConstantORM]] = {
			f"Name": SearchCriteriasORM(User.Name),
			f"Surname": SearchCriteriasORM(User.Surname),
			f"Patronymic": SearchCriteriasORM(User.Patronymic),

			f"Call_time_left": SearchCriteriasORM(User.Call_time_left),
			f"Trafic_left": SearchCriteriasORM(User.Trafic_left),
			f"SMS_left": SearchCriteriasORM(User.SMS_left),

			f"TariffName": SearchCriteriasORM(Tariff.Name),
			f"TariffPrice": SearchCriteriasORM(Tariff.Price),
			f"TariffCall_time": SearchCriteriasORM(Tariff.Call_time),
			f"TariffTrafic": SearchCriteriasORM(Tariff.Trafic),
			f"TariffSMS": SearchCriteriasORM(Tariff.SMS),
		}

	@property
	def ORM_join(self):
		Tariff = self.schema.tables.Tariff.ORM
		User = self.schema.tables.User.ORM
		q = \
			User.select(
				User.Name,
				User.Surname,
				User.Patronymic,

				User.Call_time_left,
				User.Trafic_left,
				User.SMS_left,

				Tariff.Name,
				Tariff.Price,
				Tariff.Call_time,
				Tariff.Trafic,
				Tariff.SMS,
			) \
			.join(Tariff, on=(User.TariffID == Tariff.id))
		return q


class CallDynamicSearch(DynamicSearchBaseORM):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.name: str = f"Call"
		User = self.schema.tables.User.ORM
		Call = self.schema.tables.Call.ORM
		self.search: dict[self.SearchCriteriasORM[CompareConstantORM]] = {
			f"Call_time": SearchCriteriasORM(Call.Call_time),
			f"Duration": SearchCriteriasORM(Call.Duration),

			f"FromName": SearchCriteriasORM(self.schema.alias.User_from.Name),
			f"FromSurname": SearchCriteriasORM(self.schema.alias.User_from.Surname),
			f"FromPatronymic": SearchCriteriasORM(self.schema.alias.User_from.Patronymic),

			f"ToName": SearchCriteriasORM(self.schema.alias.User_to.Name),
			f"ToSurname": SearchCriteriasORM(self.schema.alias.User_to.Surname),
			f"ToPatronymic": SearchCriteriasORM(self.schema.alias.User_to.Patronymic),
		}

	@property
	def ORM_join(self):
		User = self.schema.tables.User.ORM
		Call = self.schema.tables.Call.ORM

		User_from = self.schema.alias.User_from
		User_to = self.schema.alias.User_to

		q = \
			Call.select(
				Call.Call_time,
				Call.Duration,

				User_from.Name,
				User_from.Surname,
				User_from.Patronymic,

				User_to.Name,
				User_to.Surname,
				User_to.Patronymic,
			) \
			.join(User_from, on=(Call.User_from == User_from.id)) \
			.join(User_to, on=(Call.User_to == User_to.id))
		return q


def _test():
	pass


if __name__ == "__main__":
	_test()
