
#modeh($$LABEL$$).

#modeb(1, direct_path(var(compV), var(compV), var(compV))).
#modeb(3, comp(var(compV), const(compC))).

#modeh(invented_pred, (non_recursive)).
#modeb(invented_pred).

$$CONSTANTS$$

#bias(":- not head_not_empty.").
#bias("head_not_empty :- head(_).").
#bias(":- body(direct_path(V, _, V)).").
#bias(":- body(direct_path(V, V, _)).").
#bias(":- body(direct_path(_, V, V)).").

#maxv(5).