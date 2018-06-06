direct_path_3(C1, C2, C3) :- compV(C1), compV(C2), compV(C3), C1 != C2, C2 != C3, C1 != C3, opt_path(C1, C2, M), opt_path(C2, C3, N), val(C2, P), M & N == P.
