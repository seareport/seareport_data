# Licence for this file: APACHE
# original source: https://github.com/ManderaGeneral/generaltool/blob/bcc76a06fd6fbf1d824732939ab8698f85ee9852/generaltool/enforce_literal.py
# based on: https://stackoverflow.com/a/72832981/592289
#
# mypy: ignore-errors
# pyright: basic
from collections.abc import Callable
from sys import _getframe
from typing import Any
from typing import get_args
from typing import get_origin
from typing import Literal


def _obj_is_from_typing(obj):
    return type(obj).__name__.startswith("typing.")


def _check_value_to_literal(kwargs, name, literal):
    value = kwargs[name]
    args = get_args(literal)
    for arg in args:
        if _obj_is_from_typing(obj=arg):
            msg = f"enforce_literals does not support nested Literals in 3.8 or before. ({literal})"
            raise UserWarning(msg)
        if arg == value:
            return True
    raise AssertionError(f"'{value}' is not in {args} for '{name}'")


def _check_value_to_type(kwargs, name, type_):
    if name not in kwargs:
        return True
    if get_origin(type_) is Literal:
        _check_value_to_literal(kwargs=kwargs, name=name, literal=type_)


def enforce_literals(function: Callable[..., Any]) -> None:
    kwargs = _getframe(1).f_locals
    for name, type_ in function.__annotations__.items():
        _check_value_to_type(kwargs=kwargs, name=name, type_=type_)
