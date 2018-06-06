#modeb(1, direct_path_4(var(compV), var(compV), var(compV), var(compV)), (positive)).
#bias(":- body(direct_path_4(V, V, _, _)).").
#bias(":- body(direct_path_4(V, _, V, _)).").
#bias(":- body(direct_path_4(V, _, _, V)).").
#bias(":- body(direct_path_4(_, V, V, _)).").
#bias(":- body(direct_path_4(_, V, _, V)).").
#bias(":- body(direct_path_4(_, _, V, V)).").
#bias(":- body(direct_path_4(V1, V2, V3, V4)), not comp_in_body(V1), not comp_in_body(V2), not comp_in_body(V3), not comp_in_body(V4).").
