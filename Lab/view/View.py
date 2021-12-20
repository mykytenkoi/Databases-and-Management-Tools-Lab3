#!/usr/bin/env python
import Lab.utils
# from . import model
import enquiries
import click
# import pprint

__all___ = ["View"]


class Menu(object):
	def __init__(self, entry):
		self._entry = entry
		self._entry |= {"exit": lambda: Lab.utils.menuReturn(f"User exit")}
		self._state = None

	def __call__(self, *args, **kwargs):
		return self.loop(*args, **kwargs)

	@property
	def entry(self):
		return self._entry

	@property
	def state(self):
		return self._state

	@state.setter
	def state(self, value):
		self._state = value

	def loop(self):
		menuStack = [self.entry]
		menuChoiceStack = list()

		menuCursor = menuStack[-1]
		choice = None
		while menuStack:
			menuCursor = menuStack[-1]

			if hasattr(menuCursor, "__lab_console_interface__"):
				menu = Lab.utils.lab_console_interface(menuCursor)
			elif isinstance(menuCursor, dict):
				menu = menuCursor
			else:
				raise TypeError(f"{choice}")

			try:
				choice = enquiries.choose(menu.promt, menu)
			except Exception as e:
				print(menuCursor)
				raise e

			menuChoice = menu[choice]()

			if isinstance(menuChoice, Lab.utils.menuReturn):
				menuStack.pop()
				menuChoiceStack = menuChoiceStack[:-1]
			elif isinstance(menuChoice, Lab.utils.menuReload):
				menuStack = [self.entry]
				menuChoiceStack = list()
			elif isinstance(menuChoice, Lab.utils.menuNop):
				pass
			elif isinstance(menuChoice, Lab.utils.menuInput):
				menuChoice.func({a: click.prompt(a.column_name, type=Lab.utils.psql_types.psql_types_convert[a.data_type].type, default=a.default() if hasattr(a, "default") else Lab.utils.psql_types.psql_types_convert[a.data_type].default(), show_default=True) for a in menuChoice})
			elif isinstance(menuChoice, Lab.utils.TablePrint):
				Lab.utils.print_console_table(menuChoice.table)
				print(end=f"\n")
				print(f"{menuChoice}")
			elif menuChoice is None:
				pass
			elif menuChoice is Ellipsis:
				pass
			else:
				menuStack.append(menuChoice)
				menuChoiceStack.append(choice)

			choice = None


class View(object):
	def __init__(self, controller):
		self.controller = controller

	def mainMenu(self):
		menu = Menu(Lab.utils.lab_console_interface(self.controller))
		return menu.loop()


def _test() -> None:
	pass


if __name__ == "__main__":
	_test()
