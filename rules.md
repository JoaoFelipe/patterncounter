# Rules

This document defines the syntax of the pattern rules. There are 4 types of constructs in the syntax: Elements, Unary Operators, Binary Operators, and Groups.

## Elements

To define a pattern with elements, just write the element name. For instance to find the element `A`, the rule is just `A`. Suppose the sequence `A ... A B ... C D ... A`, this rule matches the first, second, and last groups.

In addition to simple elements, it is possible to find the group where the element was inserted. In this case, the rule that matches the insertion of an element `A` is `InA`. Suppose the sequence `A ... A B ... C D ... A`, this rule matches the first and last groups.

Similarly, it is possible to find the first group that the element does not appear anymore after appearing once. In this case, the rule that matches the removal of an element `A` is `OutA`. Suppose the sequence `A ... A B ... C D ... A`, this rule matches the third group.

Summary:

- Element: `A`
- Insertion: `InA`
- Removal: `OutA`

## Unary Operators

Unary operators can be applied to rules. Currently, three operators are supported: First (`^`), Last (`$`), and Not (`~`).

The operator First (`^`) makes the rule only match if it is at the beginning of the sequence. The rule `^A` only matches the first group in the sequence `A ... A B ... C D ... A`.

The operator Last (`$`) is similar, but it only matches at the end of the sequence. The rule `$A` only matches the last group in the sequence `A ... A B ... C D ... A`.

The operator Not (`~`) inverts matches. The rul `~A` does not match the sequence `A ... A B ... C D ... A`, because `A` has at least one match. Howerver `~E` matches the sequence.

Summary:

- First: `^A`
- Last: `$A`
- Not: `~A`

## Binary Operators

Binary operators apply to sets of rules. Currently, five operators are supported: And (` `), Intersect (`&`), Or (`|`), Sequence (`->`), LooseSequence (`=>`).

Every rule separated by space is treated as using the And operator. Hence, the rule `A C` matches the sequence `A ... A B ... C D ... A`. Note that the individual rules do not need to match in the same group: `C` matches the third group, while `A` matches the other. Since, both rules matches the sequence, `A C` also matches it. However, rules such as `A E` or `A $C` do not match the sequence.

If you want to match the rule at the same position, it is possible to use the Intersect operator (`&`). In this case, `A & B` matches only the second group of the sequence `A ... A B ... C D ... A`.

The operator Or (`|`) matches the sequence if either one of its subrules matches the sequence. The rule `E | C` matches the sequence `A ... A B ... C D ... A` because `C` matches it, even though `E` does not match it.

The Sequence operator (`->`) only matches the sequence when the second rule appears after the first one. The rule `A -> C` matches `A ... A B ... C D ... A` because `C` appears after a group that contains `A`. Note that `C -> D` does not match the sequence, since `C` and `D` are on the same group. However, `A -> B` matches the sequence because `A` matches at least a group in the sequence (the first) that appears before `B`.

The LooseSequence operator (`=>`) allows to match elements as "sequence" when they are also on the same groups. It matches everythin that the Sequence operator matches in addition to the same-group situations. In this case, `C => D` matches the sequence `A ... A B ... C D ... A`. The order within the same group does not matter. Hence, `D => C` also matches the sequence.

Summary:

- And: `A B C`
- Intersect: `A & B`
- Or: `A | B`
- Sequence: `A -> B`
- LooseSequence: `A => B`

## Groups

Finally, the last type of construct in the rules are groups. There are two types of groups: Parentheses (`()`) and Slices (`[]`, `{}`, `[}`, `{]`).

Parentheses allow nesting operators and building complex rules without worrying about operator precedences. For instance, the rule `(E | C) -> A` matches the sequence `A ... A B ... C D ... A` because it first evaluates `(E | C)` and founds that `C` matches the sequence, and then it found that `C -> A` matches the sequence. Parentheses with internal rules can be used in place of any other rule.

Slices matches sequential groups in the sequence. The rule `[A]` matches the first two groups of the `A ... A B ... C D ... A` and the last group too (slices can have size 1). In this simple form, the slice is not much more interesting than element rules. However, slices also allow finding rules within them. The rule `[A B]` matches the sequence because it finds a slice of `A` that contains `B` as well.

Is it possible to have complex rules with slices. For instance the rule `[A $B ~C]` matches a slice that does not have `C` and that ends with `B`. Hence, it matches the sequence `A ... A B ... C D ... A`. Note that the within slices, the unary operators refer to the slice groups. Hence `^` matches the first element of the slice, `$` matches the last, and `~` only considers the slice in the negative.

Square bracket slices consider all of the groups of the slices. It is also possible to match "open" slices using braces. The rule `{A B]` only matches slices of `A` that contain `B` in a position that is not the first. Similarly, the rule `[A B}` matches slices of `A` that contain `B` in a position that is not the last. Finally, the rule `{A B}` matches slices of `A` that contain `B` in a position that is neither the first nor the last.

Summary:

- Parenthesis: `(A B)`
- Closed slice: `[A B]`
- Left-open slice: `{A B]`
- Right-open slice: `[A B}`
- Open slice: `{A B}`
