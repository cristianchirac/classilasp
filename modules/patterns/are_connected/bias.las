#modeb(1, are_connected(var(compV), var(compV))).
#bias(":- body(are_connected(V, V)).").
#bias(":- body(are_connected(V1, V2)), not comp_in_body(V1), not comp_in_body(V2).").
