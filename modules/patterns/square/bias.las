#modeb(1, square(var(compV), var(compV), var(compV), var(compV)), (positive)).
#bias(":- body(square(V, V, _, _)).").
#bias(":- body(square(V, _, V, _)).").
#bias(":- body(square(V, _, _, V)).").
#bias(":- body(square(_, V, V, _)).").
#bias(":- body(square(_, V, _, V)).").
#bias(":- body(square(_, _, V, V)).").
#bias(":- body(square(V1, V2, V3, V4)), not comp_in_body(V1), not comp_in_body(V2), not comp_in_body(V3), not comp_in_body(V4).").
