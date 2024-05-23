
from unidecode import unidecode
from  .models import *
import json


def list_to_str(ls):
    result = ''
    for i in ls:
        result += i + ' \n '
    return result

 
def decode_spec(dic):
    text = ''
    for key in dic.keys():
        if type(dic[key]) is list:
            text += key + ' ' + list_to_str(dic[key]) + '\n'
        else:
            text += key + ' ' + dic[key]  + '\n'

    return text
def decode_product(dic):
    if 'name' in dic:
        name = dic['name']
        price = dic['price']
        specs = decode_spec(dic['specs'])
        return [name,price,specs]
    else:
        return dic

#########################################################################################################################
path = ['home/products/Gaming Gear/bàn phím máy tính/info.json','home/products/Gaming Gear/chuột/info.json',
        'home/products/Gaming Gear/Tai nghe chơi game/info.json','home/products/Gaming Gear/Tay cầm chơi game/info.json',
        'home/products/Linh kiện máy tính/mainboard/info.json','home/products/Linh kiện máy tính/PSU/info.json',
        'home/products/Linh kiện máy tính/Quạt tản nhiệt/info.json','home/products/Linh kiện máy tính/RAM/info.json',
        'home/products/Linh kiện máy tính/SSD/info.json','home/products/Linh kiện máy tính/VGA/info.json',
        'home/products/Linh kiện máy tính/vỏ case/info.json','home/products/Màn hình máy tính/info.json'
        ]
cate = ['Bàn phím','Chuột', 'Tai nghe chơi game','Tay cầm chơi game',
        'Bo mạch chủ','Nguồn','Quạt tản nhiệt','RAM' ,
        'SSD','VGA','Vỏ máy tính','Màn hình']
description = ['Bàn phím dành cho máy tính','Chuột máy tính', 'Tai nghe chơi game','Tay cầm chơi game',
        'Bo mạch chủ','Nguồn máy tính','Quạt tản nhiệt','Bộ nhớ trong' ,
        'Ổ cứng','Cáp màn hình','Vỏ máy tính','Màn hình máy tính']
def get_slug(str):
    str = str.lower()
    str = unidecode(str)
    str = str.replace(' ', '-')
    str = str.replace('(', '')
    str = str.replace(')', '')
    str = str.replace('/', '')
    return str

def create_categories():
    for i in range(len(cate)):
        Category.objects.create(
        title= cate[i],
        description = description[i],
        slug = get_slug(cate[i]),
        image = 'media_root/add.webp'
        )

specs = []
for p in path:
    with open(p,'r+',encoding='UTF-8') as inp:
        data = inp.read()
        specs.append(json.loads(data,object_hook=decode_product))

def add_data():
    count = 1
    for i in range(len(cate) - 1):
        for s in specs[i]:
            Item.objects.create(
                title= s[0],
                price = int(s[1]), 
                discount_price= int(s[1]),
                label = 'N',
                stock_no = 'yes',
                description_short = description[i],
                description_long = s[2],
                image = f'{s[0]}.jpg',
                image2 = f'no',
                image3 = f'no',
                is_active = True,
                category = Category.objects.get(title=cate[i]),
                slug = get_slug(s[0][:10]) + f'-{count}'
            )
            count += 1
