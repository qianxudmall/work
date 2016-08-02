# coding=utf-8
# Copyright (c) 2016 - Dmall Shanghai-Tech <sh-it@dmall.com>

import logging
import random
from dudubbo.dubbo import Dubbo
from dudubbo.dubbo.enhancetypes import Long
from dudubbo.dubbo.registry import ZookeeperRegistry


class DubboClient():
    """
    Python Library for interacting with dubbo center API
    """

    def __init__(self):
        registry = ZookeeperRegistry('192.168.90.148:2181')
        self.providers = registry.get_providers('com.wm.ware.api.ware.WareClient')
        if len(self.providers) > 0:
            dubbo_ip, dubbo_port = random.choice(self.providers).split(':')
            dubbo_port = int(dubbo_port)
            #config = {'classpath': '/home/frappe/sjerpt_o2o_verify/wmware-api-client-1.3.7.jar'}
            config = {'classpath': 'wmware-api-client-1.8.2.jar'}
            client = Dubbo(((dubbo_ip, dubbo_port),), config)
            self.dubbo_service = client.getProxy('com.wm.ware.api.ware.WareClient')

    def get_spec_rule_by_skuid(self, wareId):
        """

        return:
            List
        """

        result = None

        try:
            result = self.dubbo_service.getWareTinyInfoById(wareId);
            #result = self.dubbo_service.getSkuWareInfoBySkuIds(sku_ids)
        except Exception as e:
            return None

        if result is None or result.model is None:
            return None
        else:
            return result.model

if __name__ == "__main__":
    import pdb;pdb.set_trace()
    dubbo_client = DubboClient()
    skuid_spec_data = \
        dubbo_client.get_spec_rule_by_skuid([Long(10278694)])
    #import pdb;pdb.set_trace()
    for data in skuid_spec_data:
        print(data.wareTinyVO.itemNum)
