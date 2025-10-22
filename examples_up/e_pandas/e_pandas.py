import pandas as pd
import numpy as np
from loguru import logger

series_data = pd.Series([10, 20, 30, 40, 50],
                        index=['a', 'b', 'c', 'd', 'e'],
                        name='销售额')
logger.info(f"SERIES_DATA:\n{series_data}")
logger.info(f"INDEX:\n{series_data.index}")
logger.info(f"ARRAY:\n{series_data.array}") # ndarray
logger.info(f"VALUES:\n{series_data.values}")
logger.info(f"SHAP:\n{series_data.shape}") # (row,clu)
logger.info(f"NBYTES:\n{series_data.nbytes}") # 5x8
