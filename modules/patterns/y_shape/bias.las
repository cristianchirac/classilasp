#modeb(1, y_shape(var(compV), var(compV), var(compV), var(compV)), (positive)).
#bias(":- body(y_shape(V, V, _, _)).").
#bias(":- body(y_shape(V, _, V, _)).").
#bias(":- body(y_shape(V, _, _, V)).").
#bias(":- body(y_shape(_, V, V, _)).").
#bias(":- body(y_shape(_, V, _, V)).").
#bias(":- body(y_shape(_, _, V, V)).").
#bias(":- body(y_shape(V1, V2, V3, V4)), not comp_in_body(V1), not comp_in_body(V2), not comp_in_body(V3), not comp_in_body(V4).").
