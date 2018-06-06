triangle(C1, C2, C3) :- compV(C1), compV(C2), compV(C3), C1 != C2, C2 != C3, C3 != C1, are_connected(C1, C2), are_connected(C2, C3), are_connected(C3, C1).
