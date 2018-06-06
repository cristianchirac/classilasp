#modeb(1, triangle(var(compV), var(compV), var(compV)), (positive)).
#bias(":- body(triangle(V, _, V)).").
#bias(":- body(triangle(V, V, _)).").
#bias(":- body(triangle(_, V, V)).").
#bias(":- body(triangle(V1, V2, V3)), not comp_in_body(V1), not comp_in_body(V2), not comp_in_body(V3).").
