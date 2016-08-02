#!usr/bin/python 2.7
# -*- coding: utf-8 -*-

"本程序实现sjerpt数据在O2O中的核对"


import logging
import mysql
import duduboo
from dudubbo.dubbo.enhancetypes import Long
logging.basicConfig(level=logging.INFO,
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S',
    filename="logging_o2o_merchandise.log"
    )

dict_erp_o2o = {
    'rfId':'item_code',#物料编码
    'itemNum':'name',#国条 此字段在item barcode表中，需要数据库查找
    'title': 'item_name',#商品名称
    'brgew':'net_weight',#毛重
    'chine':'packing_name',#基本单位描述
    'place':'production_location',#商品简介：产地
    'specQt':'specification',#规格
    #'matkl':'item_group',#商品分类
    #'wareLife':'shelf_life',#保质期
    'isAuxiliaryWare':'is_auxiliary_ware',
    'refSku':'ref_sku',
    'specNum':'spec_num'

}
item = []

#从Item Barcode表中读入数据
def erp_data_item_barcode():
    conn = None
    cursor = None
    try:
        #import pdb;pdb.set_trace()
        conn = mysql.get_connection()
        cursor = conn.cursor()
        sql = "SELECT sku_id,unit_qty,ware_id,o2o_sku_id,name FROM `tabItem Barcode`"
        db_result = cursor.execute(sql)
        j = 0
        list = cursor.fetchall()
        for result in list:
            item.append({})
            item[j]['item_code'] = result[0]
            item[j]['unit_qty'] = result[1]
            item[j]['ware_id'] = result[2]
            item[j]['o2o_sku_id'] = result[3]
            item[j]['name'] = result[4]
            if item[j]['ware_id'] and item[j]['o2o_sku_id']:
                item[j]['isExist'] = 1 #在后期函数调用中通过isExist值判断是否需要进入O2O查询
            else:
                item[j]['isExist'] = 0
            j = j + 1
    except Exception as e:
        print (e)
        logging.warn(e)
    finally:
        mysql.close(conn, cursor)

def erp_data_conversion(erp_item):
    conn = None
    cursor = None
    try:
        conn = mysql.get_connection()
        cursor = conn.cursor()
        if erp_item['unit_qty'] > 1:
            # 查入数为1的o2o_sku_id
            sql = "SELECT o2o_sku_id FROM `tabItem Barcode` " \
                  "WHERE sku_id='%s' AND unit_qty='%s'" %(erp_item['item_code'],1)
            db_result = cursor.execute(sql)
            erp_item['is_auxiliary_ware'] = 1
            erp_item['ref_sku'] = cursor.fetchone()[0]
            erp_item['spec_num'] = erp_item['unit_qty']
        elif erp_item['unit_qty'] == 1:
            sql = "SELECT uom FROM `tabUOM Conversion Detail` " \
                  "WHERE parent='%s' AND conversion_factor='%s'" % (erp_item['item_code'],erp_item['unit_qty'])
            db_result = cursor.execute(sql)
            uom = cursor.fetchone()[0]
            erp_item['uom'] = uom
            if uom == 'kg' or uom == 'Kg' or uom == 'KG':
                erp_item['is_auxiliary_ware'] = 1
                # 通过uom_cd_doc2记录的入数反查Item Barcode表中的o2o_sku_id
                sql = "SELECT uom FROM `tabUOM Conversion Detail` " \
                      "WHERE parent='%s' AND (uom='%s' or uom='%s')"% (erp_item['item_code'], 'g','G')
                db_result = cursor.execute(sql)
                conversion_factor = cursor.fetchone()[0]
                sql = "SELECT o2o_sku_id FROM `tabItem Barcode` " \
                      "WHERE sku_id='%s' AND unit_qty" % (erp_item['item_code'], conversion_factor)
                db_result = cursor.execute(sql)
                o2o_sku_id = cursor.fetchone()[0]
                erp_item['ref_sku'] = o2o_sku_id
                erp_item['spec_num'] = 1000
            else:
                erp_item['is_auxiliary_ware'] = 0
                erp_item['ref_sku'] = None
                erp_item['spec_num'] = None
        else:
            pass
            # logging.warning('unit_qty=%s值存在问题'%erp_item['unit_qty'])
    except Exception as e:
        logging.info(e)
    finally:
        mysql.close(conn, cursor)
    return erp_item

def erp_data_item(erp_item):
    conn = None
    cursor = None
    try:
        conn = mysql.get_connection()
        cursor = conn.cursor()
        sql = "SELECT barcode,item_name,net_weight,packing_name,production_location,specification,item_group,shelf_life FROM `tabItem`WHERE item_code=%s"%erp_item['item_code']
        db_result = cursor.execute(sql)
        try:
            item = cursor.fetchone()
        except Exception as e:
            logging.info(e)
        #erp_item['barcode'] = item[0]
        erp_item['item_name'] = item[1]
        erp_item['net_weight'] = item[2]
        erp_item['packing_name'] = item[3]
        erp_item['production_location'] = item[4]
        erp_item['spec_count'] = item[5]
        erp_item['item_group'] = item[6]
        erp_item['shelf_life'] = item[7]
    except Exception as e:
        logging.warning(e)
    finally:
        mysql.close(conn, cursor)
    return erp_item


def compare(erp_item):
    conn = mysql.get_connection()
    cursor = conn.cursor()
    sql = "SELECT uom FROM `tabUOM Conversion Detail` " \
                 "WHERE parent='%s' AND conversion_factor='%s'" % (erp_item['item_code'],erp_item['unit_qty'])
    db_result = cursor.execute(sql)
    uom = cursor.fetchone()[0]
    erp_item['uom'] = uom
    mysql.close(conn, cursor)

    erp_item = erp_data_conversion(erp_item)
    erp_item = erp_data_item(erp_item)

    erp_item['item_code'] = str(erp_item['item_code']) + '&' +  erp_item['uom']#o2o中物料编码为item_code和uom

    dubbo_client = duduboo.DubboClient()
    #skuid_spec_data = dubbo_client.get_spec_rule_by_skuid([Long(1000210212)])
    wareid_spec_data = dubbo_client.get_spec_rule_by_ware_id([Long(erp_item['ware_id'])])
    #skuid_spec_data = skuid_spec_data1[0]
    if wareid_spec_data is not None:
        for key, value in dict_erp_o2o.items():
            if hasattr(wareid_spec_data,key):
                if erp_item[value] is not None and getattr(wareid_spec_data,key) is not None:
                    if erp_item[value] != getattr(wareid_spec_data,key):
                        logging.info('%s=%s和%s=%s不相等' 
                                     %(value,erp_item[value],key,getattr(wareid_spec_data,key)))
        #if erp_item['barcode'] is not None and wareid_spec_data.itemNum is not None:
        #    if erp_item['barcode'] != wareid_spec_data.itemNum:
        #        logging.info('barcode=%s和itemNum=%s不相等' %(erp_item['barcode'],wareid_spec_data.itemNum))
        #if erp_item['item_name'] is not None and wareid_spec_data.title is not None:
        #    if erp_item['item_name'] != wareid_spec_data.title:
        #        logging.info('item_name=%s和title=%s不相等' % (erp_item['item_name'], wareid_spec_data.title))
        #if erp_item['net_weight'] is not None and wareid_spec_data.brgew is not None:
        #    if erp_item['net_weight'] != wareid_spec_data.brgew:
        #        logging.info('net_weight=%s和brgew=%s不相等' % (erp_item['net_weight'], wareid_spec_data.brgew))
        #if erp_item['packing_name'] is not None and wareid_spec_data.chine is not None:
        #    if erp_item['packing_name'] != wareid_spec_data.chine:
        #        logging.info('packing_name=%s和brgew=%s不相等' % (erp_item['packing_name'], wareid_spec_data.chine))
        if erp_item['item_group'] is not None and wareid_spec_data.matkl is not None:
            if int(erp_item['item_group']) != int(wareid_spec_data.matkl):
                logging.info('item_group=%s和matkl=%s不相等' % (erp_item['item_group'], wareid_spec_data.matkl))
        if erp_item['shelf_life'] is not None and wareid_spec_data.wareLife is not None:
            if float(erp_item['shelf_life']) != wareid_spec_data.wareLife:
                logging.info('shelf_life=%s和wareLife=%s不相等' % (float(erp_item['shelf_life']), wareid_spec_data.wareLife))
        #if erp_item['is_auxiliary_ware'] is not None and wareid_spec_data.isAuxiliaryWare is not None:
        #    if erp_item['is_auxiliary_ware'] != wareid_spec_data.isAuxiliaryWare:
        #        logging.info('is_auxiliary_ware=%s和isAuxiliaryWare=%s不相等'
        #                     % (erp_item['is_auxiliary_ware'], wareid_spec_data.isAuxiliaryWare))
    else:
        logging.info('根据o2o_sku_id=%s未查询到数据！！！！'%Long(erp_item['o2o_sku_id']))

def main():
    import pdb;pdb.set_trace()
    erp_data_item_barcode()#从Item Barcode表中读入数据
    for data in item:
        logging.info('当前处理ware_id=%s'%data['ware_id'])
        if data['isExist'] == 0:
            logging.info('ware_id=%s或o2o_sku_id=%s存在问题' %(data['ware_id'],data['o2o_sku_id']))
            continue
        else:
            erp_item = dict()
            erp_item['item_code'] = data['item_code']
            erp_item['unit_qty'] = data['unit_qty']
            erp_item['ware_id'] = data['ware_id']
            erp_item['o2o_sku_id'] = data['o2o_sku_id']
            erp_item['name'] = data['name']
            compare(erp_item)
    # import pdb;pdb.set_trace()
    #import pdb;pdb.set_trace()
    #erp_item = dict()
    #erp_item['item_code'] = '357483'
    #erp_item['unit_qty'] = 1.0
    #erp_item['ware_id'] = '10263419'
    #erp_item['o2o_sku_id'] = '100262984'
    #compare(erp_item)

if __name__ == '__main__':
    main()
    logging.info('核对结束')
