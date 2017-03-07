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

@attr.s
class LInt():
    value = attr.ib(convert=int)

@attr.s
class LFloat():
    value = attr.ib(convert=float)

prelude = {
        "*" : op.mul,
        "-" : op.sub,
        "+" : op.add,
        "/" : op.truediv,
        "a" : LInt(34),
        "double" : lambda a: a*a
        }

@attr.s
class LIdent():
    value = attr.ib(convert=environment(prelude))

identChars = "+-_-=?~!@$*></.%^&"

expression = makeGrammar("""
    integer = ws (<digit+>:intv) ws -> LInt(intv)

    float = ws (<integer>:leftv) "." (<integer>:rightv) ws -> LFloat("%s.%s" % (leftv, rightv))

    left_paren = '('

    right_paren = ')'

    identifierChar = letter|(anything:x ?(x in identChars))

    identifier = ws (<(identifierChar)+>:ident) ws -> LIdent(ident)

    value = float|integer|identifier

    application = ws '(' ws value:name ws <(value|application)*:ids> ws ')' ws -> App(name, ids)

    expression = value|application

    """, {
            "identChars" : identChars,
            "App" : App,
            "LIdent" : LIdent,
            "LInt" : LInt,
            "LFloat" : LFloat
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

def repl():
    while True:
        parsed = expression(input("> ")).expression()
        print(parsed)
        print(evaluate(parsed))

if __name__ == "__main__":
    repl()
