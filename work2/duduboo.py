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
        #registry = ZookeeperRegistry('192.168.90.148:2181')
        #registry = ZookeeperRegistry('119.254.210.145:19901')
        registry = ZookeeperRegistry('119.254.210.145:19901?backup=119.254.210.145:19902,119.254.210.145:19903')
        self.providers = registry.get_providers('com.wm.ware.api.ware.WareClient')

        if len(self.providers) > 0:
            dubbo_ip, dubbo_port = random.choice(self.providers).split(':')
            dubbo_port = int(dubbo_port)
            config = {'classpath': '/home/frappe/sjerpt_o2o_verify/wmware-api-client-1.8.2.jar'}
            client = Dubbo(((dubbo_ip, dubbo_port),), config)
            self.dubbo_service = client.getProxy('com.wm.ware.api.ware.WareClient')

    def get_spec_rule_by_ware_id(self, ware_id):
        """

        return:
            List
        """

        result = None

        try:
            result = self.dubbo_service.getWareTinyInfoById(ware_id[0])
            #result1 = self.dubbo_service.getWareTinyInfoList(ware_id)
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
        dubbo_client.get_spec_rule_by_ware_id([Long(10278466)])
    # import pdb;pdb.set_trace()
    # for data in skuid_spec_data:
    print(skuid_spec_data)
