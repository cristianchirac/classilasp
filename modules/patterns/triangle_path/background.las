triangle_path(C1, C2, C3) :- compV(C1), compV(C2), compV(C3), C1 != C2, C2 != C3, C3 != C1, opt_path(C1, C2, M), opt_path(C2, C3, N), opt_path(C3, C1, P), val(C1, A), val(C2, B), val(C3, C), M & N == B, N & P == C, P & M == A.
