import ast
import operator

import click
from simpleeval import SimpleEval

from .search import Q


class ParseError(Exception):
    pass


class BooleanQueryType(click.ParamType):

    name = "query"

    def __init__(self):
        super().__init__()
        # Create a sandboxed evaluator allowing to use the Q object,
        # and the "|", "&" and "~" operators.
        # See: https://github.com/danthedeckie/simpleeval
        self.evaluator = SimpleEval(
            functions={"Q": Q},
            operators={
                ast.BitOr: operator.or_,
                ast.BitAnd: operator.and_,
                ast.Invert: operator.invert,
            },
        )

    def convert(self, value, param, ctx) -> Q:
        try:
            return self.evaluator.eval(value)  # 🤯
        except Exception as exc:
            raise click.BadParameter(str(exc))
