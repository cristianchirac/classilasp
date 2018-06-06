
#modeh($$LABEL$$).

$$CONSTANTS$$

#modeh(invented_pred, (non_recursive)).
#modeb(invented_pred).
#modeb(3, comp(var(compV), const(compC))).

#bias(":- not head_not_empty.").
#bias("head_not_empty :- head(_).").

#bias(":- body(comp(C, T1)), body(comp(C, T2)), T1 != T2.").
#bias(":- body(comp(C, T1)), body(naf(comp(C, T2))), T1 != T2.").
#bias("comp_in_body(V):- body(comp(V, _)).").

$$PATTERN_BIASES$$

#maxv(6).
