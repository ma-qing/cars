from cars.utils import set_redis

chezhen = {"CzcyAutoLogin": "e8y5J709aeW71cl2Iejbo2x2NdT7kcxbNzU1MTgyLCJpZCI6IjE2NDk2OCIsInRva2VuIjoiZDg3YzA4ZjQ1ZWZjYzBhOWEzYjFlN2VmZjRmZjhmNDkifQO0O0OO0O0O"}
# chezhen = {"CzcyAutoLogin": "e8y5J709aeW71cl2Iejbo2x2NdT7gc5bOTQ2MTk2LCJpZCI6IjE2MzY4NCIsInRva2VuIjoiZDgyZTdlNTFmOWJiYjUzODljYmM3NTQ1MjNhNWQ2OGIifQO0O0OO0O0O"}

def get_from_unuseless_phonenum():
    r = set_redis(2)
    # for i in r.hkeys("unuseless_cookies_car168"):
    #     r.lpush("cookies_car168_list", i)
    for k, v in r.hgetall("unuseless_cookies_car168").items():

        print(k, v)
        r.hset("cookies_car168", k, v)


if __name__ == '__main__':
    get_from_unuseless_phonenum()