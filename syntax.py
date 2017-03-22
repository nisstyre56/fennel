#! /usr/bin/env python3

from parsley import makeGrammar
from ometa.runtime import ParseError

import attr
import operator as op

def environment(env):
    return lambda ident: env.get(ident, False)

@attr.s
class App():
    proc = attr.ib()
    params = attr.ib()

@attr.s
class LStr():
    value = attr.ib()

class Number():
    @property
    def value(self):
        if self.sign == "-":
            return -self.number
        elif self.sign == "+":
            return +self.number
        elif self.sign == "None":
            return self.number
        else:
            raise ValueError("not a valid number")

@attr.s
class LInt(Number):
    number = attr.ib(convert=int)
    sign = attr.ib(convert=str)

@attr.s
class LFloat(Number):
    number = attr.ib(convert=float)
    sign = attr.ib(convert=str)

prelude = {
        "*" : op.mul,
        "-" : op.sub,
        "+" : op.add,
        "/" : op.truediv,
        "a" : LInt(34, "+"),
        "double" : lambda a: a*a
        }
@attr.s
class LOp():
    value = attr.ib(convert=environment(prelude))

@attr.s
class LIdent():
    value = attr.ib(convert=environment(prelude))

identChars = "+-_-=?~!@$*></.%^&"

with open("./syntax.parsley", "r") as syntax:
    expression = makeGrammar(syntax.read(), {
            "identChars" : identChars,
            "App" : App,
            "LIdent" : LIdent,
            "LInt" : LInt,
            "LFloat" : LFloat,
            "LOp" : LOp
         })

def evaluate(exp):
    if isinstance(exp, App):
        return evaluate(exp.proc.value)(*map(evaluate, exp.params))
    elif isinstance(exp, LInt):
        return exp.value
    elif isinstance(exp, LFloat):
        return exp.value
    elif isinstance(exp, LStr):
        return exp.value
    elif isinstance(exp, LIdent):
        return evaluate(exp.value)
    else:
        return exp

# examples
# (+ 2 a)
# (double a)
# (* 0.3 (double a))
# a
# double
# (/ 34 (+ 2 3))

def repl():
    while True:
        parsed = expression(input("> ")).expression()
        print(parsed)
        print(evaluate(parsed))

if __name__ == "__main__":
    repl()
