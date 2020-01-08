import json

with open('PRM.json', 'r', encoding='Windows-1251') as fh: #открываем файл на чтение
    data = json.load(fh) #загружаем из файла данные в словарь data

print(data)