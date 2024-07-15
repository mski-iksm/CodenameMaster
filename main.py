import luigi
import numpy as np
import gokart

import codename_master

if __name__ == '__main__':
    gokart.add_config('./conf/param.ini')
    gokart.run()
