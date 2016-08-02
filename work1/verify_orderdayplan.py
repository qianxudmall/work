#!usr/bin/python 2.7
# -*- coding: UTF-8 -*-

from __future__ import unicode_literals
import frappe
import xml.etree.ElementTree as ET
import os
import logging
logging.basicConfig(level=logging.INFO,
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S',
    filename="logging_orderdayplan.log"
    )


dict_order_cycle = {
    'OrgNO': 'org_no',
    'SupplierOrgNO': 'supplier_org_no',
    'Monday': 'monday',
    'Tuesday': 'tuesday',
    'Wednesday': 'wednesday',
    'Thursday': 'thursday',
    'Friday': 'friday',
    'Saturday': 'saturday',
    'Sunday': 'sunday'
}

def test_record(record):
    item_code = int(record.find('OrgNO').text)
    temp = int(record.find('SupplierOrgNO').text)
    logging.info('门店编号: %s' % item_code)
    # print '门店编号: %s' % item_code
    try:
        item = frappe.get_doc('Order Cycle',{'org_no':item_code,'supplier_org_no':temp})
        for key,value in dict_order_cycle.items():
            #print '调试节点'
            if int(item.get(value)) != int(record.find(key).text):
                logging.info('不一致记录: %s=%s和%s=%s' %(value,item.get(value),key,record.find(key).text))
                # print '不一致记录:%s= %s和%s= %s' % (value,item.get(value),key,record.find(key).text)
    except frappe.DoesNotExistError:
        logging.info ('找不到文件以org_no=%s和supplier_org_no=%s为条件' %(item_code,temp))


def parseXML(filename ):
    '''
    解析xml,并比较字段
    '''
    tree = ET.parse(filename)
    dataroot = tree.getroot()
    data = dataroot.iter('access')
    # data = dataroot[0].findall('REC_OrderDayPlan')
    for rec in data:
        test_record(rec)

def main():
    '''
    遍历数据文件夹,查找相应xml,并解析
    '''
    data_dir = '/home/frappe/data/20160715_1/'
    file_count = 0
    for xml_file in os.listdir(data_dir):
        if xml_file.find('REC_OrderDayPlan') != -1:
            file_count += 1
            filename = os.path.join(data_dir, xml_file)
            logging.info('处理第[%s]个文件: %s' % (file_count, filename))
            # print '处理第[%s]个文件: %s' % (file_count, filename)

            parseXML(filename)
    if file_count == 0:
        logging.info('当前目录没有OrderDayPlan文件!')
        # print '当前目录没有OrderDayPlan文件!'


if __name__ == "__main__":
    try:
        frappe.connect('sjerpt.dmall.io')
        logging.info('connected to local site')
        # print 'connected to local site'

        main()

    except Exception as e:
        logging.warning(e)
        # print e
    finally:
        frappe.destroy()
        logging.info('frappe destroyed')
        # print 'frappe destroyed'
