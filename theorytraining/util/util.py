import logging


def initLogging(thisLevel, funcLen="12"):
    log_format = ('[%(asctime)s] %(module)-15s %(funcName)-'+str(funcLen)+'s %(levelname)-8s %(message)s')
    if thisLevel == 20:
        thisLevel = logging.INFO
    elif thisLevel == 10:
        thisLevel = logging.DEBUG
    elif thisLevel == 30:
        thisLevel = logging.WARNING
    elif thisLevel == 40:
        thisLevel = logging.ERROR
    elif thisLevel == 50:
        thisLevel = logging.CRITICAL
    else:
        thisLevel = logging.NOTSET
        
    logging.basicConfig(
        format=log_format,
        level=thisLevel,
        datefmt="%H:%M:%S"
    )
