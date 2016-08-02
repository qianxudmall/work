# -*- coding:utf-8 -*-
# import frappe
import  mysql
from dudubbo.dubbo.enhancetypes import Long
import  logging
import duduboo


# 查找Item Barcode表中的记录
def get_item_barcode():
    conn = None
    cursor = None
    item_barcode_list = []
    try:
        # get mysql connection
        conn = mysql.get_connection()
        # get cursor
        cursor = conn.cursor()
        # sql
        sql = "SELECT store, sku_id, unit_qty, ware_id, o2o_sku_id FROM `tabItem Barcode`"
        db_result = cursor.execute(sql)
        for row in cursor.fetchall():
            item_barcode_list.append({
                'store': row[0],
                'sku_id': row[1],
                'unit_qty': row[2],
                'ware_id': row[3],
                'o2o_sku_id': row[4]
            })
        return item_barcode_list
    except Exception as e:
        logging.warn(e)
    finally:
        mysql.close(conn, cursor)


# UOM Conversion Detail表是Item的子表，需要通过item_code和unit_qty进行查询
def get_uom(item_code, unit_qty):

    """
    try:
        db_result = frappe.get_doc(
            'UOM Conversion Detail',
            {
                'parent': item_code,
                'conversion_factor': unit_qty
            }
        )
        if db_result:
            return db_result.get('uom')
        else:
            return ''
    except Exception as e:
        print e
    """
    conn = None
    cursor = None
    try:
        conn = mysql.get_connection()
        cursor = conn.cursor()
        sql = "SELECT uom FROM `tabUOM Conversion Detail` WHERE parent = '%s' AND unit_qty = '%s'"  % (item_code, unit_qty)
        db_result = cursor.execute(sql)
        if db_result:
            return cursor.fetchone()
        else:
            return ''
    except Exception as e:
        logging.warn(e)
    finally:
        mysql.close(conn, cursor)


# get item name from tabStore Item
def get_item_name(store_id, item_code):
    conn = None
    cursor = None
    try:
        conn = mysql.get_connection()
        cursor = conn.cursor()
        sql = "SELECT short_name FROM `tabStore Item` WHERE store_id = '%s' AND item_code = '%s'" % (store_id, item_code)
        db_result = cursor.execute(sql)
        if db_result:
            return cursor.fetchone()[0]
        else:
            return ''
    except Exception as e:
        logging.warn(e)
    finally:
        mysql.close(conn, cursor)


# get item price from tabItem Price
# condition: store_id, item_code, uom
def get_item_price(store_id, item_code, uom):
    conn = None
    cursor = None
    try:
        conn = mysql.get_connection()
        cursor = conn.cursor()
        sql = "SELECT A.price_list_rate FROM `tabItem Price` A, `tabPrice List` B WHERE A.price_list = B.price_list_name" \
              " AND B.store_id = '%s' AND A.item_code = '%s' AND A.unit = '%s'"  % (store_id, item_code, uom)
        db_result = cursor.execute(sql)
        return cursor.fetchone()[0]
    except Exception as e:
        logging.warn(e)
    finally:
        mysql.close(conn, cursor)


def main():
    dubbo_client = duduboo.DubboClient()
    skuId = get_item_barcode()[0].get('o2o_sku_id')
    print(skuId)
    skuId_spec_data = \
	dubbo_client.get_spec_rule_by_skuid([Long(skuId)])
    print(skuId_spec_data)

if __name__ == '__main__':
    main()
