#!usr/bin/python 2.7
# -*- coding: UTF-8 -*-
import frappe
import xml.etree.ElementTree as ET
import os
from datetime import datetime
import logging
logging.basicConfig(level=logging.INFO,
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S',
    filename="logging_merchpackage.log"
    )

# erp 和 sap 商品包装详情字段的 mapping 关系
dict_type_uom_detail = {
    'uom': 'PackageID',
    'parent': 'MerchID',
    'conversion_factor': 'UnitQt',
}


def test_record(record):
    #import pdb;pdb.set_trace()
    item_code = record.find('MerchID').text
    logging.info('解析商品包装数据: %s' % item_code)
    # print '解析商品包装数据: %s' % item_code
    if len(item_code) == 9 and item_code.startswith('100'):
        item_code = item_code[3:]
    try:
        ucd = frappe.get_doc('UOM Conversion Detail', {'uom': record.find('PackageID').text,'parent':item_code})
        #ucd = frappe.get_doc('UOM Conversion Detail',{'uom':record.find('PackageID').text})
        if ucd.get('conversion_factor') != float(record.find('UnitQt').text):
            logging.info('信息不一致conversion_factor=%s和UnitQt=%s' %(ucd.get('conversion_factor'),record.find('UnitQt').text))
    except frappe.DoesNotExistError:
        logging.info('找不到一致field: MerchID=%s和PackageID=%s'
                                 % (record.find('MerchID').text,record.find('PackageID').text))
        # print '找不到一致的field: PackageID=%s和MerchID=%s'% (record.find('MerchID').text,record.find('PackageID').text)

    try:
        item = frappe.get_doc('Item', {'item_code': item_code})
        if item.mini_uom != record.find('PackageID').text and float(record.find('MerchID').text) == 1.0:
            logging.info('Item中mini_uom字段未更新')
            # print  'Item中mini_uom字段未更新'
    except frappe.DoesNotExistError:
        logging.info('找不到Item_code=%s' %item_code)
        # print '找不到Item文件item_code=%s' %item_code
    except Exception as e:
        print e


def parseXML(filename ):
    '''
    解析xml,并比较字段
    '''
    tree = ET.parse(filename)
    dataroot = tree.getroot()
    data = dataroot[0][0].findall('REC_MerchPackage')
    for rec in data:
        test_record(rec)

def main():
    '''
    遍历数据文件夹,查找相应xml,并解析
    '''
    data_dir = '/home/frappe/data/20160718/'
    file_count = 0
    for xml_file in os.listdir(data_dir):
        if xml_file.find('REC_MerchPackage') != -1:
            file_count += 1
            filename = os.path.join(data_dir, xml_file)
            logging.info('处理第[%s]个文件: %s' % (file_count, filename))
            # print '处理第[%s]个文件: %s' % (file_count, filename)

            parseXML(filename)
    if file_count == 0:
        logging.info('当前目录没有REC_MerchPackage文件!')
        # print '当前目录没有REC_MerchPackage文件!'


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
