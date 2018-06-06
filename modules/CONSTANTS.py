MAX_RELEVANT_MODELS     = 1000
CLASSIFICATION_THREADS  = 10
MODELS_PER_PROC         = 1000

GENERIC_ILASP2i_CMD     = ["ILASP", "--version=2i"]
GENERIC_ILASP3_CMD      = ["ILASP", "--version=3"]
GENERIC_CLINGO_CMD      = ["clingo", "0"]
INVENTED_PREDICATES     = ["invented_pred"]
ILASP_LABEL_STRING      = "gENERIC_LABEL"

TEMP_DIR_NAME           = "__temp__"
QUERY_FILE_NAME         = "QUERY_FILE.las"
DEFAULT_QUERY_REL_PATH  = "./defaultQuery.las"
QUERY_KEY_HEAD          = "select"
QUERY_CACHE_SIZE        = 100

PER_MODEL_PREDS         = ["comp"]

RANDOM_STRING           = "Random"
QUERY_STRING            = "Query"
NO_LABEL_STRING         = "No label"
MULTIPLE_LABELS_STRING  = "Multiple labels"

MUST_LABEL_SIZE         = 50
MUST_LABEL_WEIGHT       = 2
NOT_MUST_LABEL_WEIGHT   = 1

EXAMPLE_PENALTY         = 100

PATTERNS_REL_PATH       = "./patterns/"
PATTERNS_SIGANTURES     = {
	"are_connected"        : "are_connected(V0, V1)",
	"triangle"             : "triangle(V0, V1, V2)",
	"triangle_path"        : "triangle_path(V0, V1, V2)",
	"direct_line_3"        : "direct_line_3(V0, V1, V2)",
	"direct_path_3"        : "direct_path_3(V0, V1, V2)",
	"direct_line_4"        : "direct_line_4(V0, V1, V2, V3)",
	"direct_path_4"        : "direct_path_4(V0, V1, V2, V3)",
	"y_shape"              : "y_shape(V0, V1, V2, V3)",
	"y_path"               : "y_path(V0, V1, V2, V3)",
	"y_triangle"           : "y_triangle(V0, V1, V2, V3)",
	"y_triangle_path"      : "y_triangle_path(V0, V1, V2, V3)",
	"square"               : "square(V0, V1, V2, V3)",
	"square_path"          : "square_path(V0, V1, V2, V3)",
	"square_one_diag"      : "square_one_diag(V0, V1, V2, V3)",
	"square_one_diag_path" : "square_one_diag_path(V0, V1, V2, V3)",
	"connected_4"          : "connected_4(V0, V1, V2, V3)",
	"connected_path_4"     : "connected_path_4(V0, V1, V2, V3)",
}
