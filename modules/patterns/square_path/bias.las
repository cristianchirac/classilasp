#modeb(1, square_path(var(compV), var(compV), var(compV), var(compV)), (positive)).
#bias(":- body(square_path(V, V, _, _)).").
#bias(":- body(square_path(V, _, V, _)).").
#bias(":- body(square_path(V, _, _, V)).").
#bias(":- body(square_path(_, V, V, _)).").
#bias(":- body(square_path(_, V, _, V)).").
#bias(":- body(square_path(_, _, V, V)).").
#bias(":- body(square_path(V1, V2, V3, V4)), not comp_in_body(V1), not comp_in_body(V2), not comp_in_body(V3), not comp_in_body(V4).").
