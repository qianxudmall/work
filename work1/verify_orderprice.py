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
    filename="logging_orderprice.log"
    )


# dic_oprt = {'1':"自营",'3':"联营"}
# dic_mang = {'1':"单品", '2':"金额", '3':"售价金额"}
# dic_merch = {'1':"标准",'2':"AOC", '3':"耗材",'4':"生鲜原材料",'5':"生鲜",'6':"服务",'7':"包装"}
# # dic_tax = {'0.17':"销项税%17-dmall",'0.13':"销项税%13-dmall",'0.07':"销项税%7-dmall"}
# erp 和 sap 商品类型的 mapping 关系
# dict_type = {
#     '0': '单一商品',
#     '1': '共性商品',
#     '2': '变式商品',
#     '3': '销售设备',
#     '4': '预包装',
#     '5': '展示商品',
#     '6': '组件商品',
# }

dict_item= {
    'sku':'SKU',
    'price':'NewOrderPrice',# 新价格
    'store_id':'ExeBranch_ID',  # 门店编码
    'valid_from':'StartDate',  # 生效时间
    'ext_creation':'MakeDT',
    'rec_flag':'RecFlag',
    'supplier_code':'SupplierCode',  # 供应商编号
}


def test_record(record):
    item_code = record.find('SKU').text
    # 若长度为9且有100的前缀, 则去掉100前缀
    if len(item_code) == 9 and item_code.startswith('100'):
        item_code = item_code[3:]
    db_result = frappe.db.sql(
        """SELECT sku_id FROM `tabItem Barcode` where item_barcode=%s""" % item_code)
    if db_result:
        pass
    else:
        logging.info('通过xml文件中的SKU=%s在表tabItem Barcode中没有数据' %item_code)

    try:
        price_rule = frappe.get_doc('Pricing Rule',
            {'item_code':item_code,'price':record.find('NewOrderPrice').text,
             'store':record.find('ExeBranch_ID').text,'valid_from':record.find('StartDate').text,
             'supplier':record.find('SupplierCode').text})
    except frappe.DoesNotExistError:
            logging.info('以item_code=%s，price，store，valid_from和supplier在Pricing Rule中没有数据'%item_code)


def parseXML(filename ):
    '''
    解析xml,并比较字段
    '''
    tree = ET.parse(filename)
    dataroot = tree.getroot()
    data = dataroot[0].findall('REC_OrderPriceChg')
    for rec in data:
        test_record(rec)

def main():
    '''
    遍历数据文件夹,查找相应xml,并解析
    '''
    data_dir = '/home/frappe/data/20160718'
    file_count = 0
    for xml_file in os.listdir(data_dir):
        if xml_file.find('REC_OrderPriceChg') != -1:
            file_count += 1
            filename = os.path.join(data_dir, xml_file)
            logging.info('处理第[%s]个文件: %s' % (file_count, filename))
            # print '处理第[%s]个文件: %s' % (file_count, filename)
            parseXML(filename)
    if file_count == 0:
        logging.info('当前日期没有OrgMerch文件!')
        # print '当前日期没有OrgMerch文件!'


if __name__ == "__main__":
    try:
        frappe.connect('sjerpt.dmall.io')
        logging.info('connected to local site')
        # print 'connected to local site'

        main()

    except Exception as e:
        logging.exception(e)
        # print e
    finally:
        frappe.destroy()
        logging.info('frappe destroyed')
        # print 'frappe destroyed'
