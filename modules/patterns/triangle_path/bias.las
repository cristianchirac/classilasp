#modeb(1, triangle_path(var(compV), var(compV), var(compV)), (positive)).
#bias(":- body(triangle_path(V, _, V)).").
#bias(":- body(triangle_path(V, V, _)).").
#bias(":- body(triangle_path(_, V, V)).").
#bias(":- body(triangle_path(V1, V2, V3)), not comp_in_body(V1), not comp_in_body(V2), not comp_in_body(V3).").
