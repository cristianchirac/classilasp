
#modeh($$LABEL$$).

#modeb(3, comp(var(compV), const(compC))).
#modeb(1, direct_path(var(compV), var(compV), var(compV)), (positive)).

#modeh(invented_pred, (non_recursive)).
#modeb(invented_pred).

$$CONSTANTS$$

#bias(":- not head_not_empty.").
#bias("head_not_empty :- head(_).").

#bias(":- body(comp(C, T1)), body(comp(C, T2)), T1 != T2.").
#bias(":- body(comp(C, T1)), body(naf(comp(C, T2))), T1 != T2.").
#bias(":- body(direct_path(V, _, V)).").
#bias(":- body(direct_path(V, V, _)).").
#bias(":- body(direct_path(_, V, V)).").

#bias("comp_in_body(V):- body(comp(V, _)).").
#bias(":- body(direct_path(V1, V2, V3)), not comp_in_body(V1), not comp_in_body(V2), not comp_in_body(V3).").

#maxv(6).