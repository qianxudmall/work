# coding: utf-8
from __future__ import unicode_literals
import xml.etree.ElementTree as ET
import frappe


def get_items_data(root):
    items_data = []
    for status_chg in root.iter('REC_RetailPriceChg'):
        # 如果是sku那么unit字段的单位是EA，如果是国条，那么unit字段需要通过国条找到对应的单位。
        # 长度不为6 或者 不为9的情况, 代表是国条
        items_data.append(dict(
            sku=status_chg.find('SKU').text,
            price=status_chg.find('NewSellPrice').text,  # 新价格
            store_id=status_chg.find('ExeBranch_ID').text,  # 门店编码
            valid_from=status_chg.find('StartDate').text,  # 生效时间
            rec_flag=status_chg.find('RecFlag').text,
        ))
    return items_data


def test_record(items_data):
    for item in items_data:

        if get_item_code(item) == '':
            print 'item_code数据不一致.'

        if get_item_store(item) == '':
            print 'store数据不一致.'

        try:
            item_doc = frappe.get_doc('Pricing Rule', {
                'item_code': get_item_code(item),
                'store': get_item_store(item)
                # 加上unit的查询
            })

            if item_doc.get('price') != item['price']:
                print 'price数据不一致.'

            if item_doc.get('valid_from') != item['valid_from']:
                print 'valid_from数据不一致.'
        except frappe.DoesNotExistError:
            print 'item_doc不存在.'


def get_item_code(item):
    if len(item['sku']) != 9 and len(item['sku']) != 6:
        db_result = frappe.db.sql(
            """SELECT sku_id FROM `tabItem Barcode` where item_barcode=%s AND store=%s"""
            % (item['sku'], item['store_id']))
        return db_result[0][0] if db_result else ''
    else:
        if len(item['sku']) == 9 and str(item['sku']).startswith('100'):
            return item['sku'][3:]
        else:
            return item['sku']


def get_item_store(item):
    store_db_result = frappe.db.sql('SELECT name FROM `tabStore` WHERE store_id=%s' % item['store_id'])
    item['store'] = store_db_result[0][0] if store_db_result else ''
    return item['store']


def parse_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    items_data = get_items_data(root)
    test_record(items_data)
    # print items_data

if __name__ == '__main__':
    try:
        frappe.connect('erptest')
        parse_xml('/home/dmallerp/xml/@REC_RetailPriceChg@20160514-095008-381.xml')
    except Exception as e:
        print e



