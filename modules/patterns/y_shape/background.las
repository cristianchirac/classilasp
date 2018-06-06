y_shape(C1, C2, C3, C4) :- compV(C1), compV(C2), compV(C3), compV(C4), C1 != C2, C1 != C3, C1 != C4, C2 != C3, C2 != C4, C3 != C4, are_connected(C1, C2), are_connected(C1, C3), are_connected(C1, C4).
