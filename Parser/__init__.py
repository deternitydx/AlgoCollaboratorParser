# Abey Koolipurackal (AAK4EP)
import logging
import sys

from Parser.Logger import SingleLevelFilter

logger = logging.getLogger(__name__)

stdout_handler = logging.StreamHandler(sys.stdout)
INFO_filter = SingleLevelFilter(logging.INFO, False)
stdout_handler.addFilter(INFO_filter)

detailed_formater = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler('parser.log')
file_handler.setFormatter(detailed_formater)

logger.addHandler(stdout_handler)
logger.addHandler(file_handler)

logger.setLevel(logging.DEBUG)