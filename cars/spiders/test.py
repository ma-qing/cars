import requests

from cars.utils import Mysqlpython, set_redis

r = set_redis()
url = "http://www.chehang168.com/index.php?c=index&m=Cardata"
headers = {
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
        "Host": "www.chehang168.com",
        # "Cookie": "DEVICE_ID=77cd83d79707a7fb386f712f2bef8db0; _uab_collina=158894954478649638062081; soucheAnalytics_usertag=RI8C9Ol6w8; U=1769515_8fb8933d8591166ea0b616db963ba427"
        "Cookie":"DEVICE_ID=77cd83d79707a7fb386f712f2bef8db0; _uab_collina=158894954478649638062081; soucheAnalytics_usertag=RI8C9Ol6w8; U=1769515_8fb8933d8591166ea0b616db963ba427"

    }
# cookeis = {
# "DEVICE_ID":"77cd83d79707a7fb386f712f2bef8db0",
# "_uab_collina":"158894954478649638062081",
# "soucheAnalytics_usertag":"RI8C9Ol6w8",
# "U":"1769515_8fb8933d8591166ea0b616db963ba427",
#
# }
dbhelper = Mysqlpython()


def set_data_db():
    result = requests.get(url=url, headers=headers)
    dicts = eval(result.text[14:])
    for brand_encode, v in dicts.items():
        print("编码品牌名", brand_encode)
        for index,(i,m) in enumerate(v.items()):
            # 第一层记录了名字
            if index == 0:
                global brand
                brand = m[2:]
                print("品牌名:", brand)
                continue
            for j,h in m.items():
                # j 是内层数据键值，目前不知道啥作用，h是对应类型的编码和类性质
                # 统一的类型名是h.get('name')
                unity_type = h.get("name")
                for encode_type, cartype in h.get('pserise').items():
                    print("编码品牌值:", encode_type, "类型名", cartype.get("name"))
                    sql = "insert into car168_style (brand, brand_encode, unity_type, `type`, type_encode) values(%s, %s, %s, %s, %s)"
                    dbhelper.execute(sql, [brand, brand_encode.strip("'"), unity_type, cartype.get("name"), encode_type.strip("'")])


def set_data_toredis():
    sql = "select id, brand, brand_encode, unity_type, `type`, type_encode from car168_style"
    sql_result = dbhelper.readall(sql)
    for result in sql_result:
        print(result)
        r.set(result[5], result[4])
# url = "http://www.chehang168.com/index.php?c=index&m=allBrands"
# proxy = {
#     "http":"http://202.115.142.147:9200",
#     # "https":"http://202.115.142.147:9200",
# }
# result = requests.get(url=url, head)ers=headers, stream=True)
# # print(result.text)
# print(result.raw._connection.sock.getpeername()[0])
# print(result.text)
if __name__ == '__main__':
    # set_data_toredis()
    print([i.decode() for i in r.keys()])