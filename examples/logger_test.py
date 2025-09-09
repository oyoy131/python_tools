from loguru import logger
LOG_FILE = "../storage/log.txt"

logger.add(LOG_FILE)

if __name__ == "__main__":
    logger.info("test info")
    logger.success("test success")
    logger.warning("test warning")
    logger.debug("test debug")
    """
    TRACE (5)
    DEBUG (10)
    INFO (20)
    SUCCESS (25)
    WARNING (30)
    ERROR (40)
    CRITICAL (50)
    """
    logger.log(10,"log")
