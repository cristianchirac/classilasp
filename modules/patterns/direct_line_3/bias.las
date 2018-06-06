#modeb(1, direct_line_3(var(compV), var(compV), var(compV)), (positive)).
#bias(":- body(direct_line_3(V, _, V)).").
#bias(":- body(direct_line_3(V, V, _)).").
#bias(":- body(direct_line_3(_, V, V)).").
#bias(":- body(direct_line_3(V1, V2, V3)), not comp_in_body(V1), not comp_in_body(V2), not comp_in_body(V3).").
