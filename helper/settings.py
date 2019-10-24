import json
import random
# Python 字典类型转换为 JSON 对象
data = {
    'no': 1,
    'name': 'Runoob',
    'url': 'http://www.runoob.com',
    "dict": {
        'no': 1,
        'name': 'Runoob',
        'url': 'http://www.runoob.com'
    }
}

# 写入 JSON 数据
with open('data.json', 'w') as f:
    json.dump(data, f)

# 读取数据
with open('data.json', 'r') as f:
    data = json.load(f)
    for json_data in data:
        print(json_data)
        if isinstance(data[json_data], dict):
            print(data[json_data])

