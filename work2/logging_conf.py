#! /usr/bin/python
# -*- coding:utf-8 -*-
# 日志配置文件

import logging

logging.basicConfig(level=logging.INFO,
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S',
)
