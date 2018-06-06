#modeb(1, y_path(var(compV), var(compV), var(compV), var(compV)), (positive)).
#bias(":- body(y_path(V, V, _, _)).").
#bias(":- body(y_path(V, _, V, _)).").
#bias(":- body(y_path(V, _, _, V)).").
#bias(":- body(y_path(_, V, V, _)).").
#bias(":- body(y_path(_, V, _, V)).").
#bias(":- body(y_path(_, _, V, V)).").
#bias(":- body(y_path(V1, V2, V3, V4)), not comp_in_body(V1), not comp_in_body(V2), not comp_in_body(V3), not comp_in_body(V4).").
