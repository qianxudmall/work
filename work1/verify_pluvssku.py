#!usr/bin/python 2.7
# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
import frappe
import xml.etree.ElementTree as ET
import os
from datetime import datetime
import logging
logging.basicConfig(level=logging.INFO,
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S',
    filename="logging_pluvssku.log"
    )

dict_plu_detail= {
    'item_barcode': 'PLU',
    'store': 'OrgNO',
    'sku_id': 'MerchID',
    'uom': 'UOM',
    'retail_price': 'RetailPrice',
    'unit_qty': 'IncludeSKU',
}

def test_record(record):
    sku_id = record.find('MerchID').text
    item_code = sku_id
    if len(sku_id) == 9 and sku_id.startswith('100'):
        item_code = sku_id[3:]
    try:
        item_barcode = frappe.get_doc('Item Barcode',{'item_barcode':record.find('PLU').text,'store':record.find('OrgNO').text})
      
        if item_barcode.get('unit_qty') != int(record.find('IncludeSKU').text):
            logging.info('unit_qty=%s和IncludeSKU=%s不相等' %(item_barcode.get('unit_qty'),record.find('IncludeSKU').text))
        if item_barcode.get('sku_id') != item_code:
            logging.info('sku_id=%s和MerchID=%s不相等'%(item_barcode.get('sku_id'),item_code))
        else:
            try:
                temp = float(record.find('IncludeSKU').text)
                uom_coinversion_detail = frappe.get_doc('UOM Conversion Detail',
                                     {'conversion_factor':temp,'parent':item_code})
            #except Exception as e:
                # print '根据conversion_factor=%s在UOM Conversion Detail中未查到数据'%record.find('IncludeSKU').text
            #    logging.info('根据conversion_factor=%s和store=%s在UOM Conversion Detail中未查到数据'
            #                       %(record.find('IncludeSKU').text,sku_id)
                try:
                    item_price = frappe.get_doc('Item Price',{'item_code':item_code ,
                                                  'unit':uom_conversion_detail.uom})
                    if item_price.get('price_list_rate') != float(record.find('RetailPrice').text):
                        logging.info('以item_code=%s和unit=%s查找价格price_list_rate=%s与RetailPrice=%s' 
                                          %(item_code,uom_conversion_detail.uom,item_price.get('price_list_rate'),
                                            record.find('RetailPrice').text))
                        # print '不一致价格: %s和%s' % (item_price.get('price_list_rate'), record.find('RetailPrice').text)
                except Exception as e:
                    logging.info("根据item_code=%s和unit=%s在Item Price中未查到数据" \
                                 % (item_code,uom_conversion_detail.uom))
            except Exception as e:
                 logging.info('未找到文件conversion_factor=%s和store=%s' 
                             %(record.find('IncludeSKU').text,sku_id))
    except frappe.DoesNotExistError:
        logging.info('根据item_barcode=%s和store=%s在Item Barcode中未查到数据' 
                    %(record.find('PLU').text,record.find('OrgNO').text))
        # print '根据item_code=%s和unit=%s在Item Price中未查到数据' %(item_code,uom_conversion_detail.uom)




def parseXML(filename ):
    '''
    解析xml,并比较字段
    '''
    tree = ET.parse(filename)
    dataroot = tree.getroot()
    data = dataroot[0][0].findall('REC_PLUvsSKU')
    for rec in data:
        test_record(rec)

def main():
    '''
    遍历数据文件夹,查找相应xml,并解析
    '''
    data_dir = '/home/frappe/data/20160718/'
    file_count = 0
    #import pdb;pdb.set_trace()
    #for xml_file in os.listdir(data_dir):
    #    if xml_file.find('REC_PLUvsSKU') != -1:
    #        file_count += 1
    #        filename = os.path.join(data_dir, xml_file)
    #        logging.info('处理第[%s]个文件: %s' % (file_count, filename))
            # print '处理第[%s]个文件: %s' % (file_count, filename)

    #        parseXML(filename)
    parseXML('/home/frappe/data/20160718/@REC_PLUvsSKU@20160624-111748-195.xml')
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
        #raise e
        logging.warning(e)
        # print e
    finally:
        frappe.destroy()
        logging.info('frappe destroyed')
        # print 'frappe destroyed'
