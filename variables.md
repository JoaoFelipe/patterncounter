# Variables

This document describes the syntax of variable definitions (argument `-v` of command line).

There are three types of variable definitions:

- **Simple** (`-v "X"`): If you just define the name of the variable, the tool will try to bind it to all names that appear in your input file
- **Exclusive** (`-v "X~A,B"`): If you define a list of comma-separated elements after `~`, the tool will try to bind the variable to all names that appear in your input file, **except** the ones on the list
- **Inclusive** (`-v "X:A,B"`): If you define a list of comma-separated elements after `:`, the tool will **only** bind the variable to the elements you defined.

It is not necessary to define `In` and `Out` variables. If you have a variable `X` bound to `Element`, not only the rule `X` will match `Element`, but the rule `InX` will match `InElement` and the rule `OutX` will match `OutElement`.
