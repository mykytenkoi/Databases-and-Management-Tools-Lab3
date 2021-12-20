#!/usr/bin/env python
import Lab.view
import Lab.model
import Lab.utils
import peewee

__all__ = ["Controller"]


class Controller(object):
	def __init__(self, dbconf: dict[str], model=Lab.model, view=Lab.view):
		self._dbconf = dbconf
		self._dbconn = peewee.DatabaseProxy()
		self._model = model
		self._view = view.View(self)
		self._schema = Lab.model.Telecommunications(self._dbconn)

	@property
	def schema(self):
		return self._schema

	def start(self) -> None:
		with peewee.PostgresqlDatabase(**self._dbconf, autoconnect=True, autocommit=True, autorollback=True) as conn:
			self._dbconn.initialize(conn)
			self._view.mainMenu()

	@property
	def __lab_console_interface__(self):
		MVC = 1
		if not MVC:
			result = Lab.utils.lab_console_interface(self.schema)
			# result |= {f"exit": Lab.utils.menuReturn(f"User exit"), }
		else:
			result = Lab.utils.LabConsoleInterface({
				**{f'"{table.table}" table': (lambda table: lambda: Lab.utils.LabConsoleInterface({
					f"describe": table.describe,
					f"show data": table.showData,
					f"add data": table.addData,
					f"edit data": table.editData,
					f"remove data": table.removeData,
					f"random fill": table.randomFill,
					f"return": lambda: Lab.utils.menuReturn(f"User menu return"),
				}, promt=table.promt))(table) for table in self.schema},
				f'Schema "{self.schema}" utils': lambda: Lab.utils.LabConsoleInterface({
					f"reinit": self.schema.reinit,
					f"random fill": self.schema.randomFill,
					f"return": lambda: Lab.utils.menuReturn(f"User menu return"),
				}, promt=f'Schema "{self.schema}" utils'),
				f'Dynamic search': lambda: Lab.utils.LabConsoleInterface({
					**{dynamicsearch.name: (lambda dynamicsearch: lambda: Lab.utils.LabConsoleInterfaceDynamicUpdate(lambda: Lab.utils.LabConsoleInterface({
						**{search_name: (lambda search_name, search: lambda: Lab.utils.LabConsoleInterfaceDynamicUpdate(lambda: Lab.utils.LabConsoleInterface({
							**{f"Property {property_id} {property_instance}": (lambda property_id, property_instance: lambda: Lab.utils.LabConsoleInterfaceDynamicUpdate(lambda: Lab.utils.LabConsoleInterface({
								f"ignore": property_instance.reset,
								f"<": property_instance._lt,
								f"<=": property_instance._le,
								f"=": property_instance._eq,
								f"!=": property_instance._ne,
								f">=": property_instance._ge,
								f">": property_instance._gt,
								f"LIKE": property_instance._like,
								f"set NULL": property_instance.setNull,
								f"set constant": property_instance.setConstant,
								f"return": lambda: Lab.utils.menuReturn(f"User menu return"),
							}, promt=property_instance.promt)))(property_id, property_instance) for property_id, property_instance in enumerate(search.search_criterias.append(), 1)},
							f"return": lambda: Lab.utils.menuReturn(f"User menu return"),
						}, promt=search.promt)))(search_name, search) for search_name, search in dynamicsearch.search.items()},
						f"execute": dynamicsearch.execute,
						f"sql": lambda: print(dynamicsearch.sql),
						f"reset": dynamicsearch.reset,
						f"return": lambda: Lab.utils.menuReturn(f"User menu return"),
					}, promt=dynamicsearch.promt)))(dynamicsearch) for dynamicsearch in self.schema.dynamicsearch.values()},
					f"return": lambda: Lab.utils.menuReturn(f"User menu return"),
				}, promt=f"""Schema "{self.schema}" dynamic search interface"""),
			}, promt=f'MVC schema "{self.schema}" interface')
			# result = Lab.utils.LabConsoleInterface({}, promt=f'MVC schema "{self.schema}" interface')
		return result


def _test() -> None:
	pass


if __name__ == "__main__":
	_test()
