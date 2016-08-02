#!usr/bin/python 2.7
# -*- coding: UTF-8 -*-

from __future__ import unicode_literals
import frappe
import xml.etree.ElementTree as ET
import os
from datetime import datetime
import logging
import fnmatch

logging.basicConfig(level=logging.INFO,
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S',
    filename="logging_merchandise.log"
    )

# dic_oprt = {'1':"自营",'3':"联营"}
# dic_mang = {'1':"单品", '2':"金额", '3':"售价金额"}
# dic_merch = {'1':"标准",'2':"AOC", '3':"耗材",'4':"生鲜原材料",'5':"生鲜",'6':"服务",'7':"包装"}
# # dic_tax = {'0.17':"销项税%17-dmall",'0.13':"销项税%13-dmall",'0.07':"销项税%7-dmall"}

dict_type = {
    '0': '单一商品',
    '1': '共性商品',
    '2': '变式商品',
    '3': '销售设备',
    '4': '预包装',
    '5': '展示商品',
    '6': '组件商品',
}


dict_item= {
    #'item_code': 'MerchID',
    'item_name': 'MerchName',
    'brand': 'Trademark',
    'packing_name': 'PackingName',
    #'spec_count': 'Specification',
    #'spec_unit': 'SpecUnit',
    'production_location': 'ProducingArea',
    #'barcode': 'BarCode',
    'shelf_life': 'ShelfLife',
    #'length': 'Length',
    #'width': 'Width',
    #'height': 'High',
    #'net_weight': 'Weight',
    #'type': 'Type',
    #'mini_sale_unit': 'IsMiniSale ',
    'remark': 'Remark',
    'packing_qty': 'SubUnit',
}


def test_record(record):
    item_code = record.find('MerchID').text
    logging.info('对比门店商品: %s' % item_code)
    # print '对比商品主数据: %s' % item_code
    # 若长度为9且有100的前缀, 则去掉100前缀
    if len(item_code) == 9 and item_code.startswith('100'):
        item_code = item_code[3:]
    try:
        item = frappe.get_doc('Item',{'item_code':item_code})
    except Exception as e:
        logging.info(e)
    else:
        #import pdb;pdb.set_trace()
        for key,value in dict_item.items():
            if item.get(key) != record.find(value).text:
                logging.info('不一致field: %s=%s和%s=%s' %(key,item.get(key),value,record.find(value).text))
                # print '不一致field: %s' % key
        #if item.get('spec_count') != int(record.find('Specification').text):
        #    logging.info('数据不一致spec_count=%s和Specification=%s' %(item.get('spec_count'),record.find('Specification').text))
        if item.get('barcode') != record.find('BarCode').text:
            logging.info('barcode=%s和BarCode=%s数据不一致' %(item.get('barcode'),record.find('BarCode').text))
        if item.get('length') != float(record.find('Length').text):
            logging.info('length=%s和Length=%s不一致' %(item.get('length'),record.find('Length').text))
        if item.get('width') != float(record.find('Width').text):
            logging,info('width=%s和Width=%s数据不一致' %(item.get('width'),record.find(Width).text))
        if item.get('height') != float(record.find('High').text):
            logging.info('height=%s和high=%s不一致' %(item.get('height'),record.find('High').text))
        if item.get('net_weight') != float(record.find('Weight').text):
            logging.info('net_weight=%s和Weight=%s数据不一致' %(item.get('net_weight'),record.find('weight').text))
        temp = item.get('type')
        temp1 = record.find('Type').text
        if temp != dict_type[temp1]:
            logging.info('商品类型不一样:%s和%s' %(temp,dict_type[temp1]))
            # print '商品类型不一样:%s和%s' %(dict_type[temp],dict_type[temp1])
        item_specification = record.find('Specification').text + record.find('SpecUnit').text
        if item.get('specification') != item_specification:
            logging.info('specification值不相等%s and %s'%(item.get('specification'),item_specification))


def parseXML(filename ):
    '''
    解析xml,并比较字段
    '''
    tree = ET.parse(filename)
    dataroot = tree.getroot()
    data = dataroot.iter('REC_Merchandise')
    #data = dataroot[0][0].findall('REC_Merchandise')
    for rec in data:
        test_record(rec)

def main():
    '''
    遍历数据文件夹,查找相应xml,并解析
    '''
    #data_dir = '/home/frappe/frappe-bench/sites/sjerp_verify_test/'
    data_dir = '/home/frappe/data/20160718/'
    file_count = 0
    for xml_file in os.listdir(data_dir):
        if fnmatch.fnmatch(xml_file,'@REC_Merchandise@*.xml'):
        #if xml_file.find('REC_Merchandise') != -1:
            file_count += 1
            filename = os.path.join(data_dir, xml_file)
            logging.info('处理第[%s]个文件: %s' % (file_count, filename))
            # print '处理第[%s]个文件: %s' % (file_count, filename)

            parseXML(filename)
    if file_count == 0:
        logging.info('当前日期没有OrgMerchandise文件!')
        # print '当前日期没有OrgMerch文件!'


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
