y_triangle_path(C1, C2, C3, C4) :- compV(C1), compV(C2), compV(C3), compV(C4), C1 != C2, C1 != C3, C1 != C4, C2 != C3, C2 != C4, C3 != C4, opt_path(C1, C2, M), opt_path(C1, C3, N), opt_path(C1, C4, P), opt_path(C3, C4, Q), val(C1, A), val(C3, B), val(C4, C), M & N == A, N & P == A, M & P == A, N & Q = B, P & Q = C.
