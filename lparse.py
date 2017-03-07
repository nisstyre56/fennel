#! /usr/bin/env python3

from parsley import makeGrammar
from ometa.runtime import ParseError
from sys import argv
import attr
import operator as op

ops = {
        "*" : op.mul,
        "-" : op.sub,
        "+" : op.add,
        "/" : op.truediv
        }

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

@attr.s
class LIdent():
    value = attr.ib()

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

    """, {
            "identChars" : identChars,
            "App" : App,
            "LIdent" : LIdent,
            "LInt" : LInt,
            "LFloat" : LFloat
         })

def evaluate(exp):
    if isinstance(exp, App):
        return ops[exp.proc](*map(evaluate, exp.params))
    else:
        return int(exp)

print(expression(" ".join(argv[1:])).application())
#print(evaluate(expression(" ".join(argv[1:])).application()))
