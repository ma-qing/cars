import json

from cars.utils import set_redis
r = set_redis(2)
cookies168_list = [# IP:  202.115.142.147:9200
# call: 17112460114
{
"DEVICE_ID":"7e0bb1e828c608755e912939ba82ffae",
"_uab_collina":"158988569645805597623073",
"soucheAnalytics_usertag":"6BQzfShr4E",
"U":"1769515_8fb8933d8591166ea0b616db963ba427",
},

# 17112460115
# 本机
{
"DEVICE_ID":"1080dab04fa992cceda99cb170f242c7",
"_uab_collina":"158987070291212374204157",
"soucheAnalytics_usertag":"mBAvxk7evo",
"U":"1774074_c420d2eae812c202ccdfb114ea1fc17f",
},

{# 17112460103
"DEVICE_ID":"67e213653b85e55b9accad82ac1882cf",
"_uab_collina":"158987181384118818389311",
"soucheAnalytics_usertag":"OKq8IyXzZp",
"U":"1727488_39646d7ebad7b4c1280a6053db69c34c",
},

{
# 17112460112
"DEVICE_ID":"42d0fa4859cd922a2069a16cf8525fe5",
"_uab_collina":"158987228278179034888569",
"soucheAnalytics_usertag":"SKg56kxnvU",
"U":"1717724_7fdd133c2c97bb1eec96694afa62e244",
},
{#17112460106
"DEVICE_ID":"df6c36b857432f08302fe91e7f170a54",
"_uab_collina":"158987336582652455647216",
"soucheAnalytics_usertag":"dzwHz0UNFc",
"U":"1774139_0b162bcac947db998e7f75b66dda8c75",
},
]


cookies168_list2 = [
#  {
# "DEVICE_ID":"40a0fa91be838fb8823352f3241b5c47",
# "_uab_collina":"158989563213926247920875",
# "soucheAnalytics_usertag":"LJqkH5UUeF",
# "U":"1771509_112194f98be47bf05a4e1f118bba69db",
#  }
{"DEVICE_ID":"4704484da024b2682342c6699f95b85e",
"_uab_collina":"158981448277521896061991",
"soucheAnalytics_usertag":"B9cfK1uQz7",
"U":"1724517_5ca1cd2dbeb31c700df5f43c94adc74e",
 },
#16574984721

]
cookies = {
    # "16574984721":{
    # "DEVICE_ID":"33cfbf18b521a159ab4a937b2fb24ebb",
    # "U":"1783002_1e1145e57390a23b054e623dbac7b14d"
    # },
    # "17030033875":{
    # "DEVICE_ID":"77cd83d79707a7fb386f712f2bef8db0",
    # "U":"1782990_c41c7269512a00396129d4e56c68124f",
    # },
    # "17112460114":{
    # "DEVICE_ID":"6afe870dde798775c2d9b6320f920980",
    # "U":"1769515_8fb8933d8591166ea0b616db963ba427",
    # },
    # "17112460115":{
    # "DEVICE_ID":"0a5cbc2f7c8726add9a3d345515f6d09",
    # "U":"1774074_c420d2eae812c202ccdfb114ea1fc17f",
    # },

# "17112460105":{
#     "DEVICE_ID":"c8936d43abb07e39fd81ec055f5b9bdd",
#     "U":"1774096_f3e0d61569e9c49a2cee55e92ac0739d",
#     },
# "17112460113":{
#     "DEVICE_ID":"731c116ffdae59616221598cb4758536",
#     "U":"1724517_5ca1cd2dbeb31c700df5f43c94adc74e",
#     },
#
# "17112460103":{
#     "DEVICE_ID":"3124ff557f724915c8ba92e5c160a113",
#     "U":"1727488_39646d7ebad7b4c1280a6053db69c34c",
#     },
# "17112460107":{
#     "DEVICE_ID":"929ed332adfa2bc72d49a795c4732d2d",
#     "U":"1768840_a60b0f889dde1d4c6e7d14943b019e82",
#     },
# "17112460112":{
#     "DEVICE_ID":"4123a15a5b970bcb723433845b20026b",
#     "U":"1717724_7fdd133c2c97bb1eec96694afa62e244",
#     },
# "17061084093":{
#     "DEVICE_ID":"088e5044cd51202c116bbe44cf7d8739",
#     "U":"1721193_f782af159d2652dc952080e7f02384c8",
#     },
# "17061084095":{
#     "DEVICE_ID":"7881076035177cc86243e9c708fa2533",
#     "U":"1750071_a769eccc47c00f2d35a6fdffaf14f5c9",
#     },
# "16733208014":{
#     "DEVICE_ID":"6e71ad4a165dccffda4ac2b6c93320e4",
#     "U":"1765801_6aa1a1f2d7df9b9b1c8254c678566c3b",
#     },
#
# "16733208042":{
#     "DEVICE_ID":"8f972da1d0feba429606730f8f0bb132",
#     "U":"1766029_1fec6b8a7928d56ca1eff21990fed86e",
#     },
# "16733207994":{
#     "DEVICE_ID":"5887ff86b3f77ed8e4fed1d8319625e0",
#     "U":"1750080_3db61d3f3d78f776a0c55705b4c5789e",
#     },

# "16574980930":{
#     "DEVICE_ID":"9cb78a638c4e3634f9ef84615a7657e2",
#     "U":"1790323_179bae3c4e560c35112398efae03cb07",
#     },
"16531165344":{
    "DEVICE_ID":"76bccdd90ef81161228ac8b068520b6c",
    "U":"1790035_14e3d47c7b0c72c55d2df61739fa97db",
    },

}
for k, v in cookies.items():
    mapping = {json.dumps(v):int(k)}
    print(mapping)
    r.zadd("cookies_car168", mapping)