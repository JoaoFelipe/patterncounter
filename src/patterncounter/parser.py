"""Parses pattern definition string and builds operator"""

from typing import List, Type, Union
from .operators import Sequence, First, Last, Not, Has, Rule, And, Slice


TokenList = List[Union[Rule, str]]


def index_of(list_obj: TokenList, value: str) -> int:
    """Returns position of string in token list or -1"""
    try:
        return list_obj.index(value)
    except ValueError:
        return -1 


def process_operators(tokens: TokenList) -> Rule:
    """Processes token list and returns combined Rule"""
    if not tokens:
        raise ValueError("Invalid syntax: operator split mismatch")
    if (pos := index_of(tokens, '->')) != -1:
        return Sequence(process_operators(tokens[:pos]), process_operators(tokens[pos+1:]))
    if (pos := index_of(tokens, '=>')) != -1:
        return Sequence(process_operators(tokens[:pos]), process_operators(tokens[pos+1:]), same=True)    
    if (pos := index_of(tokens, '|')) != -1:
        return process_operators(tokens[:pos]) | process_operators(tokens[pos+1:])
    if (pos := index_of(tokens, '&')) != -1:
        return process_operators(tokens[:pos]) ^ process_operators(tokens[pos+1:])
    
    new_tokens: List[Rule] = []
    stack: List[Type[Union[First, Last, Not]]] = []
    for token in tokens:
        if token == "^":
            stack.append(First)
        elif token == "$":
            stack.append(Last)
        elif token == "~":
            stack.append(Not)
        else:
            if isinstance(token, str):
                token = Has(token)
            while stack:
                token = stack.pop()(token)
            new_tokens.append(token)
    if stack:
        raise ValueError("Invalid syntax: invalid operator position")
    if len(new_tokens) > 1:
        return And(*new_tokens)
    return new_tokens[0]


def tokenize(text: str) -> List[str]:
    """Tokenizes string into a list of tokens"""
    tokens: List[str] = []
    current: List[str] = []
    for letter in text:
        if letter in "{[()]}|&^$~":
            if current:
                tokens.append(''.join(current))
                current = []
            tokens.append(letter)
        elif letter in "-=":
            if current:
                tokens.append(''.join(current))
            current = [letter]
        elif letter == ">":
            current.append(letter)
            tokens.append(''.join(current))
            current = []
        elif letter == " ":
            if current:
                tokens.append(''.join(current))
                current = []    
        else:
            current.append(letter)
    if current:
        tokens.append(''.join(current))
    return tokens

    
def parse(text: str) -> Rule:
    """Parses text and returns a Rule"""
    tokens = tokenize(text)
    stack: List[TokenList] = [[]]
    for token in tokens:
        if token in "({[":
            stack.append([token])
        elif token in ")}]":
            if len(stack) == 1:
                raise ValueError(f"Invalid syntax: extra {token} found")
            temp = stack.pop()
            
            result: Rule
            if isinstance(temp[0], str) and temp[0] in "{[":
                if not isinstance(temp[1], str) or temp[1] in "|&^$~->=>":
                    raise ValueError("Invalid syntax: operator not supported as first element of slice")
                result = Slice(temp[1], open_first=temp[0] == "{", open_last=token == "}")
                temp = temp[2:]
                if temp:
                    inner = process_operators(temp)
                    result << inner
            else:
                temp = temp[1:]
                result = process_operators(temp)
            stack[-1].append(result)
        else:
            stack[-1].append(token)
    if len(stack) != 1:
        raise ValueError("Invalid syntax: unclosed group/slice")
    return process_operators(stack[-1])
