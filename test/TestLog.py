from time import time

from xkits import cmds

if __name__ == "__main__":
    cmds.initiate_logger(logger=cmds.logger)
    end = time() + 100
    while time() < end:
        cmds.logger.info(int(time() / 3))
