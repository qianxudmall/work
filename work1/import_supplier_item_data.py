# coding=utf-8

from __future__ import unicode_literals
import xml.etree.ElementTree as ET
import frappe
import argparse
import logging
import os
import fnmatch

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='test.log',  # 日志文件
                    filemode='w')

# 配置日志：在终端输出
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

# xml and erp mapping: REC_DCVSMerch ==> Supplier Item
dict_supplier_item = {
    'supplier': 'OrgNO1',
    'store': 'OrgNO2',
    'merch_id': 'MerchID',
    'order_tax': 'OrderTaxRate',
    'cost_price': 'CostPrice',
    'allow_purchase': 'AllowPurchase',
    'allow_return': 'AllowReturn',
    'return_uom': 'RtnAddress',
    'min_qty': 'MinQuantity',
    'order_package_id': 'OrderPackageID',
    'delivery_days': 'DeliverDays'
}


def get_tax_account(tax_rate):
    if tax_rate == '0':
        return '进项税0% - dmall'
    elif tax_rate == '0.13':
        return '进项税13% - dmall'
    elif tax_rate == '0.17':
        return '进项税17% - dmall'


def allow_purchase(purchase_code):
    return True if purchase_code == '1' else False


def allow_return(return_code):
    return True if return_code == '1' else False


# import supplier item data from REC_DCVSMerch.xml
def import_supplier_item_data(root, file_name):
    for supplier_item in root.iter(file_name):
        new_supplier_item = {}
        for key, value in dict_supplier_item.items():
            element = supplier_item.find(value)
            new_supplier_item[key] = element.text if element is not None else None

        if len(new_supplier_item['merch_id']) == 9 and new_supplier_item['merch_id'].startswith('100'):
            new_supplier_item['merch_id'] = new_supplier_item['merch_id'][3:]

        if len(new_supplier_item['supplier']) == 9 and new_supplier_item['supplier'].startswith('100'):
            new_supplier_item['supplier'] = new_supplier_item['supplier'][3:]

        new_supplier_item['order_tax'] = get_tax_account(new_supplier_item['order_tax'])
        new_supplier_item['allow_purchase'] = allow_purchase(new_supplier_item['allow_purchase'])
        new_supplier_item['allow_return'] = allow_return(new_supplier_item['allow_return'])

        try:
            supplier_item_doc = frappe.get_doc('Supplier Item',
                                               {
                                                   'supplier': new_supplier_item['supplier'],
                                                   'merch_id': new_supplier_item['merch_id'],
                                                   'store': new_supplier_item['store']
                                               })
            if supplier_item_doc:
                # test_record(supplier_item_doc, new_supplier_item)

                if supplier_item_doc.get('order_tax') != new_supplier_item['order_tax']:
                    logging.info('order_tax数据不一致：(frappe:%s, XML:%s)\r\n'
                                 % (supplier_item_doc.get('order_tax'), new_supplier_item['order_tax']))

                if supplier_item_doc.get('cost_price') != new_supplier_item['cost_price']:
                    logging.info('cost_price数据不一致:(frappe:%s, XML:%s) \r\n'
                                 % (supplier_item_doc.get('cost_price'), new_supplier_item['cost_price']))

                if supplier_item_doc.get('allow_purchase') != new_supplier_item['allow_purchase']:
                    logging.info('allow_purchase数据不一致:(frappe:%s, XML:%s) \r\n'
                                 % (supplier_item_doc.get('allow_purchase'), new_supplier_item['allow_purchase']))

                if supplier_item_doc.get('allow_return') != new_supplier_item['allow_return']:
                    logging.info('allow_return数据不一致:(frappe:%s, XML:%s) \r\n'
                                 % (supplier_item_doc.get('allow_return'), new_supplier_item['allow_return']))

                if (supplier_item_doc.get('return_uom')).lower() != (new_supplier_item['return_uom'][2:]).lower():
                    logging.info('return_uom数据不一致:(frappe:%s, XML:%s)\r\n'
                                 % (supplier_item_doc.get('return_uom'), new_supplier_item['return_uom']))
                if supplier_item_doc.get('min_qty') != new_supplier_item['min_qty']:
                    logging.info('min_qty数据不一致:(frappe:%s, XML:%s) \r\n'
                                 % (supplier_item_doc.get('min_qty'), new_supplier_item['min_qty']))

                if supplier_item_doc.get('order_package_id') != new_supplier_item['order_package_id']:
                    logging.info('order_package_id数据不一致:(frappe:%s, XML:%s)\r\n'
                                 % (supplier_item_doc.get('order_package_id'), new_supplier_item['order_package_id']))

                if supplier_item_doc.get('delivery_days') != new_supplier_item['delivery_days']:
                    logging.info('delivery_days数据不一致:(frappe:%s, XML:%s)\r\n'
                                 % (supplier_item_doc.get('delivery_days'), new_supplier_item['delivery_days']))

        except frappe.DoesNotExistError:
            logging.info('Supplier Item does not exist in frappe. \r\n')


def parse_xml(xml_file, file_name):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        import_supplier_item_data(root, file_name)

    except Exception as e:
        logging.info(e)


def main():
    try:
        logging.info('try connecting...\r\n')
        frappe.connect('sjerpt.dmall.io')
        logging.info('connect successfully...\r\n')
        parser = argparse.ArgumentParser()
        parser.add_argument("filename", help="method type")
        args = parser.parse_args()
        # parser.add_argument("file_dir", help="the dir of xml file"
        # 遍历文件夹, 找到需要导入的所有文件
        data_dir = '/home/frappe/data/20160718/'
        for xml_file in os.listdir(data_dir):
            if fnmatch.fnmatch(xml_file, '@'+args.filename+'@*.xml'):
                file_path = os.path.join(data_dir, xml_file)
                logging.info('开始导入文件 %s' % file_path)
                parse_xml(file_path, args.filename)
    except Exception as e:
        logging.info(e)
    finally:
        logging.info('destroy frappe connection \r\n')
        frappe.destroy()


if __name__ == '__main__':
    main()
