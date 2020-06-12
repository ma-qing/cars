# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import logging

from cars.log_utils import SelfLog

import pymysql

from cars.utils import Mysqlpython, set_redis, MYDB, HOST, USER, PASSWD, charset

class MysqlPipeline(object):
    save_url_r = set_redis(db=1)
    def open_spider(self, spider):
        self.conn = pymysql.connect(
            host=HOST,
            port=3306,
            db=MYDB,
            user=USER,
            password=PASSWD,
            charset=charset,
        )
        self.cur = self.conn.cursor()

    def close_spider(self, spider):
        self.cur.close()
        self.conn.close()

    def process_item(self, item, spider):

        selflog = SelfLog(spider.name)
        selflog_error = SelfLog("error")
        keys = ["brand", "type", "year", "style", "guide_price", "displacement", "configuration", "version", "status"]
        values = [item[i] for i in keys]
        # 插入车型数据前先在数据库中进行匹配是否存在，若存在则判断是否符合更新条件进行更新， 若不存在则保存
        sql_search_style = "select id, brand, type from car_style where brand=%s and type=%s and year=%s and style=%s and guide_price=%s"
        search_db_result = Mysqlpython().readall(sql_search_style, [item["brand"], item['type'], item['year'], item['style'], item['guide_price']])

        if search_db_result:
            commit_id = search_db_result[0][0]
            # selflog.logger.info("出现的重复车型:%s", search_db_result[0])
            update_set = "update car_style set status=null "
            update_where = " where id=%s "
            sqlparam = [commit_id]

            if not item['guide_price'] and item['guide_price'] != "None":
                update_set += " , guide_price=%s"
                update_where += " and (guide_price is null or guide_price='None')"
                sqlparam.append(item['guide_price'])
            if not item['displacement'] and item['displacement'] != "None":
                update_set += " , displacement=%s"
                update_where += " and (displacement is null or displacement='None')"
                sqlparam.append(item['displacement'])
            if item['version'] and item['version'] != "None":
                update_set += " , version=%s"
                update_where += " and (version is null or version='None')"
                sqlparam.append(item['version'])
            # 如果update_set 还是原来的值则不执行更新操作
            if update_set == "update car_style set status=null ":
                pass
            else:
                sql_update = update_set + update_where
                # selflog.logger.info(
                #     "执行更新sql:{sql_update}, values:{values}, id:{commit_id}".format(sql_update=sql_update,
                #                                                                    values=sqlparam,
                #                                                                    commit_id=commit_id))
                try:
                    self.cur.execute(sql_update, sqlparam)
                    self.conn.commit()
                except Exception as e:
                    selflog_error.logger.error(
                        "更新sql出错:{sql_update}, values:{values}, id:{commit_id},e:{e}".format(sql_update=sql_update,
                                                                                             values=sqlparam,
                                                                                             commit_id=commit_id, e=e))
        # 如果查不到则进行插入车型、价钱、更新时间等详情操作
        else:
            # 插入车型表
            sql = "insert into `{}` ({}) values ({})".format(
                item.table_name,
                ','.join(keys),
                # 使用占位符插入的方式是保证兼容除字符串格式以外数据
                ','.join(['%s'] * len(values)),
            )
            try:
                self.cur.execute(sql, values)
                self.conn.commit()
            except Exception as e:
                selflog_error.logger.info("{spidername} 插入车型表出错e:{e}sql:{sql}, --values:{values}".format(
                    spidername=spider.name,
                    e=e,
                    sql=sql,
                    values=values
                ))
                commit_id = None
            else:
                commit_id = self.cur.lastrowid

        # 如果没有车价格和交易量则不进行插入
        if commit_id and (item['price'] or item['volume']):

            # 在redis中判断这个详情页hash: detail-url: 更新时间##数据库保存id是否存在，
            # 如果存在则判断更新时间是否符合，不过不符合则进行数据插入然后更新redis数据
            # 如果不存在则存入redis和数据库
            requesturl = item['detail_url']
            rediskey = item['rediskey']
            # 从 中取出更新时间和保存的id
            hash_value = self.save_url_r.hget(rediskey, requesturl)
            if hash_value:
                hash_value = hash_value.decode()
                updatetime = hash_value.split('##')[0]
                save_id = hash_value.split('##')[1]

                if updatetime == item['updatetime']:
                    pass
                # 执行插入
                else:
                    self.insert_detaildata(spider, commit_id, item, selflog_error, rediskey)
                #     sql_update_detail = "update car_detail set updatetime=%s, price=%s, volume=%s where id=%s".format(
                #         updatetime=item['updatetime'], price=item['price'],volume=item['volume'], save_id=save_id)
                #     sql_insert_detail = "insert "
                #     try:
                #         self.cur.execute(sql_insert_detail, [item['updatetime'], item['price'],item['volume'], save_id])
                #         # 更新redis的值
                #         self.save_url_r.hset(rediskey, requesturl, item['updatetime'] + "##" + str(self.cur.lastrowid))
                #         print("{spidername}--更新爬取价格数据:{updata}".format(spidername=spider.name, updata=item['updatetime'] + "##" + save_id))
                #
                #         # selflog.logger.info("更新爬取价格数据:{updata}".format(updata=item['updatetime'] + "##" + save_id))
                #     except Exception as e:
                #         selflog_error.logger.error("{spidername}更新爬取车价详情出错e:{e}__sql:{sql}".format(spidername=spider.name, e=e, sql=sql_update_detail))
            # redis中查不到这条数据，直接写入数据库中， 并在redis中添加 detail_url:更新时间##save_id 数据
            else:
                self.insert_detaildata(spider, commit_id, item, selflog_error, rediskey)
                # selflog.logger.info("写入爬取价格数据:{updata}".format(updata=item['updatetime'] + "##" + str(self.cur.lastrowid)))

                    # self.save_url_r.sadd(item['rediskey'], requesturl)

        else:
            selflog.logger.info("没有交易价格和交易量数据，car_detial表不进行插入key:%s, --values:%s"%(keys, values))
        return item


    def insert_detaildata(self, spider, commit_id, item, selflog_error, rediskey):
        table_name = "car_detail"
        second_key = ["platform", "vehicleType", "price", "volume", "updatetime", "detail_url"]
        second_values = [item['platform'], commit_id, item['price'], str(item['volume']), item['updatetime'],
                         item['detail_url']]

        # 插入车型平台价格详情表
        second_sql = "insert into `{}` ({}) values ({})".format(
            table_name,
            ','.join(second_key),
            ','.join(['%s'] * len(second_values))
        )
        try:
            self.cur.execute(second_sql, second_values)
            self.conn.commit()
            cardetail_id = self.cur.lastrowid
        except Exception as e:
            selflog_error.logger.info(
                "{spidername} 插入车价详情error:{e}--style表中的id:{id}--出错的sql:{second_sql}, --values:{second_values}".format(
                    spidername=spider.name,
                    e=e,
                    id=commit_id,
                    second_sql=second_sql,
                    second_values=second_values
                ))
        else:
            self.save_url_r.hset(rediskey, item['detail_url'], item['updatetime'] + "##" + str(self.cur.lastrowid))
