import re
import json
from datetime import datetime
import os
from collections import defaultdict

def get_store_name(tab):
    return tab[0]

def ends_with_upper_letter(word):
    if (word[-1].isupper()): return True
    else: return False

def get_price(tab):
    if (bool(re.match(r'^[A-Z]$', tab[-1]))): 
        del tab[-1]
        price = tab[-1]
    else:
        price = tab[-1][:-1]
    tab[-1] = ""
    return price

def amount_price_check(word):
    pattern = r'^\d+.*[*x×]\d+[,\.]\d{2}$'
    return bool(re.match(pattern, word))

def tax_letter_check(tab):
    for word in tab:
        pattern = r'^[A-Z]$'
        if (bool(re.match(pattern, word))):
            return True

def wrong_endline_check(word):
    pattern = r'^\d[,\.]\d{2}.'
    return bool(re.match(pattern, word))

def get_store(store_name):
    return store_name[0]

def get_amount_price(tab):
    amount_price = tab[-2]
    tab[-2] = ""
    for i in range(3,5):
        if (amount_price_check(amount_price)): break
        else: 
            amount_price = tab[-i] + amount_price
            tab[-i] = ""
    return amount_price

def get_information(tab):
    price = get_price(tab)
    amount_price = get_amount_price(tab)
    name = ""
    for k in tab:
        name = name + k
    if (tax_letter_check(tab)): name = name[:-1]
    return price, amount_price, name

def price_format_check(word):
    pattern = r'.*[.\,].*'
    return bool(re.match(pattern, word))

def get_products(products_list):
    data = []
    for m in range(0, len(products_list)):
        tab = products_list[m].split(" ")
        price = ""
        amount_price = ""
        name = ""
        discount = ""
        # All data are included in single line
        if (len(tab)>=4 and (ends_with_upper_letter(tab[-1]) or wrong_endline_check(tab[-1]))):
            price, amount_price, name = get_information(tab)
            if (price_format_check(amount_price)!=True):
                price = ""
                amount_price = ""
                name = ""
        # Looking for discount
        elif ("-" in products_list[m]):
            for k in tab:
                if "-" in k:
                    discount = k[1::]
                    break
        # Data are separated into 2 rows
        elif (m!=0):
            tmp = products_list[m-1] + " " + products_list[m]
            tab = tmp.split(" ")
            if (len(tab)>=4 and (ends_with_upper_letter(tab[-1]) or wrong_endline_check(tab[-1]))):
                price, amount_price, name = get_information(tab)
        data.append([name, amount_price, price, discount])
    return data

def amount_price_separation(word):
    pattern1 = r'[0-9]'
    amount = ""
    price = ""
    counter = 0
    while (True):
        if (bool(re.match(pattern1, word[counter]))): 
            amount += word[counter]
            counter += 1
            if (bool(re.match(r'^[,\.]$', word[counter]))): 
                amount += word[counter]
                counter += 1
        else: break
    while (True):
        if (not bool(re.match(pattern1, word[counter]))): 
            counter += 1
        else: break
    price = word[counter::]
    return amount, price

def clear_data(data):
    new_data = []
    for i in range(0, len(data)):
        if (data[i][0]!="" and data[i][3]==""):
            amount, price = amount_price_separation(data[i][1])
            if (i!=len(data)-1 and data[i+1][0]+data[i+1][1]+data[i+1][2]=="" and data[i+1][3]!=""):
                new_data.append(
                    [data[i][0], 
                     float(amount.replace(",",".")), 
                     float(price.replace(",",".")), 
                     float(data[i][2].replace(",",".")), 
                     float(data[i+1][3].replace(",","."))])
            else: 
                new_data.append(
                    [data[i][0], 
                     float(amount.replace(",",".")), 
                     float(price.replace(",",".")), 
                     float(data[i][2].replace(",",".")), 
                     0])
    del data
    return new_data

def get_price_total(word):
    tab = word.split(" ")
    return float(tab[-1].replace(",","."))

def create_receipt(store_name, date, products, total_price):
    receipt = {
        "store": store_name,
        "date": date,
        "products": [],
        "total": total_price
    }

    for product in products:
        product_dict = {
            "name": product[0],
            "amount": product[1],
            "price": product[2],
            "total": product[3],
            "discount": product[4]
        }
        receipt["products"].append(product_dict)

    receipt_json = json.dumps(receipt, ensure_ascii=False, indent=4)
    return receipt_json

def parse_receipt(json_string):
    data = json.loads(json_string)

    store_name = data.get("store")
    date = data.get("date")
    products = data.get("products", [])
    total_price = data.get("total")

    return store_name, date, products, total_price

def get_date():
    date = datetime.now()
    date = date.strftime("%d-%m-%Y %H:%M:%S")
    return date

def suma_rabatow(lista):
    if not lista or any(len(row) < 4 for row in lista):
        raise ValueError("Lista musi zawierać co najmniej dwa wiersze i dwie kolumny.")

    suma = 0
    
    for wiersz in lista:
        rabat = wiersz[-1]
        cena = wiersz[-2]
        roznica = cena - rabat
        suma += roznica

    return suma

def append_receipt_to_db(receipt, db_filename="receipts_db.json"):
    if not os.path.exists(db_filename):
        current_data = {"receipts": []}
    else:
        with open(db_filename, "r", encoding="utf-8") as f:
            current_data = json.load(f)

    current_data["receipts"].append(receipt)

    with open(db_filename, "w", encoding="utf-8") as f:
        json.dump(current_data, f, ensure_ascii=False, indent=4)

def get_receipts(db_filename="receipts_db.json"):
    if not os.path.exists(db_filename):
        return []
    
    with open(db_filename, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    if "receipts" in data:
        return data["receipts"]
    else:
        print("Brak paragonów w pliku. Zwracam pustą listę.")
        return []

def delete_receipt_by_date(date, db_filename="receipts_db.json"):
    if not os.path.exists(db_filename):
        print("Plik z paragonami nie istnieje. Nie można usunąć paragonu.")
        return False
    
    with open(db_filename, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    if "receipts" not in data:
        print("Brak paragonów do usunięcia.")
        return False
    
    receipts = data["receipts"]
    original_length = len(receipts)
    
    updated_receipts = [r for r in receipts if r["date"] != date]
    
    if len(updated_receipts) == original_length:
        print("Nie znaleziono paragonu z podaną datą.")
        return False
    
    data["receipts"] = updated_receipts
    with open(db_filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print("Paragon z datą", date, "został usunięty.")
    return True

def generate_store_statistics_with_prices(store_name, db_filename="receipts_db.json"):
    if not os.path.exists(db_filename):
        print("Plik z paragonami nie istnieje. Nie można wygenerować statystyk.")
        return {}

    with open(db_filename, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "receipts" not in data:
        print("Brak paragonów w pliku.")
        return {}

    product_totals = defaultdict(float)

    product_price_set = set()

    for receipt in data["receipts"]:
        if receipt["store"] == store_name:
            for product in receipt["products"]:
                product_name = product["name"]
                product_quantity = product["amount"]
                product_price = product["price"]

                product_identifier = f"{product_name}_{product_price}"

                if product_identifier not in product_price_set:
                    product_price_set.add(product_identifier)
                    product_totals[product_name] += product_quantity
                else:
                    if f"{product_name}_old_price" not in product_totals:
                        product_totals[f"{product_name}_old_price"] += product_quantity
                    else:
                        product_totals[f"{product_name}_old_price"] += product_quantity

    return dict(product_totals)