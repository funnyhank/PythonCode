import logging
import logging.config


logging.config.fileConfig('logging.conf')

rootLogger = logging.getLogger()
rootLogger.debug('This is debug')

logger = logging.getLogger('fileLogger')
logger.info('this is info')