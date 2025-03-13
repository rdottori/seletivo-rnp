import logging
import sys

def setup_logger():
# Configura logger
# Output: retorna objeto de logger pronto pra uso
	logger = logging.getLogger("viaipe")

	#logger.setLevel(logging.INFO)
	logger.setLevel(logging.DEBUG)

	handler = logging.StreamHandler(sys.stdout)
	formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
	handler.setFormatter(formatter)

	logger.addHandler(handler)
	return logger

# Logger pra ser importanto e usado por outras partes do programa
logger = setup_logger()
