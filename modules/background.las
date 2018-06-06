compV(C) :- comp(C, _).
compV(C) :- comp(_, C, _).

edge(P1, P2) :- edge(P2, P1).
are_connected(C1, C2) :- port(C1, P1), port(C2, P2), edge(P1, P2).

opt_path(C1, C2, M + N) :- are_connected(C1, C2), val(C1, M), val(C2, N).
opt_path(C1, C2, M + N - P) :- opt_path(C1, C3, M), opt_path(C3, C2, N), val(C3, P), M & N == P.
