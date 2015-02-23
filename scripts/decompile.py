#!/usr/bin/env python
#
# A script for decompiling files by using the retdec.com public REST API
# (https://retdec.com/api/). Internally, it uses the retdec-python library
# (https://github.com/s3rvac/retdec-python), which is assumed to be installed
# and available for import.
#
# Copyright: (c) 2015 by Petr Zemek <s3rvac@gmail.com> and contributors
# License: MIT, see the LICENSE file for more details
#

import sys

from retdec.tools import decompile

if __name__ == '__main__':
    sys.exit(decompile.main())
