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
                    filename='verify_test.log',  # 日志文件
                    filemode='w')

# 配置日志：在终端输出
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-8s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)


# xml and erp mapping: REC_MerchBOM ==> Item Component
dict_merch_bom = {
    'merch_id': 'MerchID',
    'component': 'CompMerchID',
    'component_qty': 'CompQty',
    'comp_package': 'CompPackageID'
}

# xml and erp mappinp: REC_MerchStatusChg ==> Item Status Change
dict_merch_status_change = {
    'org_id': 'OrgNO',
    'chg_id': 'ChgID', # 变更单号
    'merch_id': 'MerchID',
    'start_date': 'StartDate',
    'new_status': 'NewStatus',
    'can_order_opl': 'CanOrder_OPL',
    'can_order_manual': 'CanOrder_Manual',
    'can_order_promo': 'CanOrder_Promo',
    'can_order_sto': 'CanOrder_STO',
    'can_sale': 'CanSale',
    'pr_style': 'PRStyle',
    'deleted': 'Deleted',
    'create_price_chg': 'CreatePriceChg',
    'price_chg_interval': 'PriceChgInterval',
    'price_chg_count': 'PriceChgCount',
    'price_chg_rate': 'PriceChgRate',
    'ext_input_datetime': 'InputDT'
}
# xml and erp mapping: REC_Organization ==> Supplier
dict_supplier = {
    'supplier_id': 'OrgNo',
    'supplier_name': 'OrgName',
    'supplier_type': 'OrgStyle',
    'bank': 'BankName',
    'bank_account': 'Accounts',
    'tax_number': 'TaxNumber',
    'is_purchase_allowed': 'BSID',
    'self_buyer': 'SelfBuyer',
    'address': 'Address',
    'telephone': 'Telephone',
    'email': 'Email'
}

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


# 开始导入item_component的数据
def import_item_component_data(root):

    for merch_bom in root.iter('REC_MerchBOM'):
        # create a new item component
        new_item_component = {}
        # component_count += 1
        for key, value in dict_merch_bom.items():
            element = merch_bom.find(value)
            new_item_component[key] = element.text if element is not None else None

        new_item_component['component_qty'] = float(new_item_component['component_qty']) \
            if new_item_component['component_qty'] else 0.0

        # 对merch_id做处理，如果长度为9并且以100开头，则去掉100
        if len(new_item_component['merch_id']) == 9 and new_item_component['merch_id'].startswith('100'):
            new_item_component['merch_id'] = new_item_component['merch_id'][3:]

        # 对component处理，如果长度为9并且以100开头，去掉前缀100
        if len(new_item_component['component']) == 9 and new_item_component['component'].startswith('100'):
            new_item_component['component'] = new_item_component['component'][3:]

        try:
            item_component_doc = \
                frappe.get_doc('Item Component',
                               {
                                   'merch_id': new_item_component['merch_id'],
                                   'component': new_item_component['component']
                               })

            if item_component_doc:
                if item_component_doc.get('component_qty') != new_item_component['component_qty']:
                    logging.info('component_qty数据不一致: (frappe:%s, XML:%s)\r\n'
                                 % (item_component_doc.get('component_qty'), new_item_component['component_qty']))

                if item_component_doc.get('comp_package') != new_item_component['comp_package']:
                    logging.info('comp_package数据不一致: (frappe:%s, XML:%s)\r\n'
                                 % (item_component_doc.get('comp_package'), new_item_component['comp_package']))

        except frappe.DoesNotExistError:
            logging.info('item component %s can not found.' % new_item_component['merch_id'])


# 开始导入REC_MerchStatusChange的数据
def import_merch_status_change_data(root):

    # iterator
    for merch_status_change in root.iter('REC_MerchStatusChg'):
        new_merch_status_change = {}
        for key, value in dict_merch_status_change.items():
            element = merch_status_change.find(value)
            new_merch_status_change[key] = element.text if element is not None else None

        # 如果merch_id的长度为9，并且以100开头，则去掉100
        if len(new_merch_status_change['merch_id']) == 9 and new_merch_status_change['merch_id'].startswith('100'):
            new_merch_status_change['merch_id'] = new_merch_status_change['merch_id'][3:]

        try:
            merch_status_chg_doc = \
                frappe.get_doc('Item Status Change',
                               {
                                   'org_id': new_merch_status_change['org_id'],
                                   'chg_id': new_merch_status_change['chg_id']
                               })

            if merch_status_chg_doc:

                if merch_status_chg_doc.get('org_id') != new_merch_status_change['org_id']:
                    logging.info('org_id数据不一致:(frappe:%s,XML:%s)\r\n'
                                 % (merch_status_chg_doc.get('org_id'), new_merch_status_change['org_id']))

                if merch_status_chg_doc.get('merch_id') != new_merch_status_change['merch_id']:
                    logging.info('merch_id数据不一致: (frappe:%s, XML:%s)\r\n'
                                 % (merch_status_chg_doc.get('merch_id'), new_merch_status_change['merch_id']))

                if merch_status_chg_doc.get('chg_id') != new_merch_status_change['chg_id']:
                    logging.info('chg_id数据不一致:(frappe:%s, XML:%s)\r\n'
                                 % (merch_status_chg_doc.get('chg_id'), new_merch_status_change['chg_id']))

                if merch_status_chg_doc.get('start_date') != new_merch_status_change['start_date']:
                    logging.info('start_date数据不一致:(frappe:%s, XML:%s)\r\n'
                                 % (merch_status_chg_doc.get('start_date'), new_merch_status_change['start_date']))

                if merch_status_chg_doc.get('new_status') != new_merch_status_change['new_status']:
                    logging.info('new_status数据不一致:(frappe:%s, XML:%s)\r\n'
                                 % (merch_status_chg_doc.get('new_status'), new_merch_status_change['new_status']))

                if merch_status_chg_doc.get('can_order_opl') != new_merch_status_change['can_order_opl']:
                    logging.info('can_order_opl数据不一致:(frappe:%s, XML:%s)\r\n'
                                 % (merch_status_chg_doc.get('can_order_opl'),
                                    new_merch_status_change['can_order_opl']))

                if merch_status_chg_doc.get('can_order_manual') != new_merch_status_change['can_order_manual']:
                    logging.info('can_order_manual数据不一致:(frappe:%s, XML:%s)\r\n'
                                 % (merch_status_chg_doc.get('can_order_manual'),
                                    new_merch_status_change['can_order_manual']))

        except frappe.DoesNotExistError:
            logging.info('Merch status change doc does not exist in frappe')


# import supplier data from REC_Organization.xml
def import_supplier_data(root):
    for supplier_data in root.iter('REC_Organization'):
        new_supplier = {}
        for key, value in dict_supplier.items():
            element = supplier_data.find(value)
            new_supplier[key] = element.text if element is not None else None
        try:
            supplier_doc = \
                frappe.get_doc('Supplier',
                            {
                                'supplier_id': new_supplier['supplier_id']
                            })
            if supplier_doc:

                if supplier_doc.get('supplier_name') != new_supplier['supplier_name']:
                    logging.info('supplier_name数据不一致：(frappe:%s, XML:%s)\r\n'
                                 % (supplier_doc.get('supplier_name'), new_supplier['supplier_name']))

                if supplier_doc.get('supplier_type') != new_supplier['supplier_type']:
                    logging.info('supplier_type数据不一致：(frappe:%s, XML:%s)\r\n'
                                 % (supplier_doc.get('supplier_type'), new_supplier['supplier_type']))

                if supplier_doc.get('bank') != new_supplier['bank']:
                    logging.info('bank数据不一致：(frappe:%s, XML:%s)\r\n'
                                 % (supplier_doc.get('bank'), new_supplier['bank']))

                if supplier_doc.get('bank_account') != new_supplier['bank_account']:
                    logging.info('bank_account数据不一致：(frappe:%s, XML:%s)\r\n'
                                 % (supplier_doc.get('bank_account'), new_supplier['bank_account']))

                if supplier_doc.get('tax_number') != new_supplier['tax_number']:
                    logging.info('tax_number数据不一致：(frappe:%s, XML:%s)\r\n'
                                 % (supplier_doc.get('tax_number'), new_supplier['tax_number']))

                if supplier_doc.get('is_purchase_allowed') != new_supplier['is_purchase_allowed']:
                    logging.info('is_purchase_allowed数据不一致：(frappe:%s, XML:%s)\r\n'
                                 % (supplier_doc.get('is_purchase_allowed'), new_supplier['is_purchase_allowed']))

                if supplier_doc.get('self_buyer') != new_supplier['self_buyer']:
                    logging.info('self_buyer数据不一致：(frappe:%s, XML:%s)\r\n'
                                 % (supplier_doc.get('self_buyer'), new_supplier['self_buyer']))

                if supplier_doc.get('address') != new_supplier['address']:
                    logging.info('address数据不一致：(frappe:%s, XML:%s)\r\n'
                                 % (supplier_doc.get('address'), new_supplier['address']))

                if supplier_doc.get('telephone') != new_supplier['telephone']:
                    logging.info('telephone数据不一致：(frappe:%s, XML:%s)\r\n'
                                 % (supplier_doc.get('telephone'), new_supplier['telephone']))

                if supplier_doc.get('email') != new_supplier['email']:
                    logging.info('email数据不一致：(frappe:%s, XML:%s)\r\n'
                                 % (supplier_doc.get('email'), new_supplier['email']))

        except frappe.DoesNotExistError:
            logging.info('Supplier does not exist in frappe.\r\n')


# 定义方法的dict
dict_method_type = {
    '1': import_item_component_data,
    '2': import_merch_status_change_data,
    '3': import_supplier_data,
}

# xml 数据类型和 xml 字段的 mapping 关系
type_xml_field_mapping = {
    '1': 'REC_MerchBOM',
    '2': 'REC_MerchStatusChg',
    '3': 'REC_Organization',
}


def parse_xml(method_type, xml_file):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        dict_method_type[method_type](root)
    except Exception as e:
        logging.info(e)


def main():
    try:
        logging.info('try connecting...\r\n')
        frappe.connect('sjerpt.dmall.io')
        logging.info('connect successfully...\r\n')
        parser = argparse.ArgumentParser()
        parser.add_argument("type", help="method type")
        args = parser.parse_args()
        # parser.add_argument("file_dir", help="the dir of xml file")

        # 遍历文件夹, 找到需要导入的所有文件
        data_dir = '/home/frappe/data/20160718/'
        for xml_file in os.listdir(data_dir):
            if fnmatch.fnmatch(xml_file, '@'+type_xml_field_mapping[args.type]+'@*.xml'):
                file_path = os.path.join(data_dir, xml_file)
                logging.info('开始导入文件 %s' % file_path)
                parse_xml(args.type, file_path)
    except Exception as e:
        logging.info(e)
    finally:
        logging.info('destroy frappe connection \r\n')
        frappe.destroy()


if __name__ == '__main__':
    main()
