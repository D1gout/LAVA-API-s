import hashlib
import hmac
import json
import random
import string

import requests

from config import shop_id, secret_key      # shop_id - id Магазина, secret_key - Ключ аккаунта

s = requests.session()


def HeaderGen(data):    # Генерация Header
    json_str = json.dumps(data).encode()

    sign = hmac.new(bytes(secret_key, 'UTF-8'), json_str, hashlib.sha256).hexdigest()

    header = {
        'Signature': sign,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    return header


def OrderGen():     # Генерация Уникального id для Запросов
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))

    return random_string


class LavaPayment:
    def __init__(self):
        self.base_url = 'https://api.lava.ru/'

    def PostAvailableTariffs(self):     # Доступные тарифы
        __URL = self.base_url + 'business/invoice/get-available-tariffs'

        data = {
            'shopId': shop_id
        }

        req = s.post(__URL, json=data, headers=HeaderGen(data))

        req = json.loads(req.text)

        return req

    def PostCreateInvoice(self, request_sum):       # Создание платежа
        __URL = self.base_url + 'business/invoice/create'

        gen_order_id = OrderGen()

        data = {
            "shopId": shop_id,
            "sum": request_sum,
            "orderId": gen_order_id,
            "successUrl": "Ссылка на вашего бота",
            "failUrl": "Ссылка на вашего бота",
            "expire": 10,    # Время жизни ссылки
            "comment": "Пополнение баланса",
            "includeService": ["card", "sbp", "qiwi"]       # Доступные методы
        }

        req = s.post(__URL, json=data, headers=HeaderGen(data))

        req = json.loads(req.text)
        req = req['data']['url']

        return [req, gen_order_id]

    def PostStatusInvoice(self, order_id):      # Статус платежа
        __URL = self.base_url + 'business/invoice/status'

        data = {
            'orderId': order_id,
            'shopId': shop_id
        }

        req = s.post(__URL, json=data, headers=HeaderGen(data)).text

        req = json.loads(req)
        try:
            req = req['data']['status']

            return req  # success, created
        except TypeError:
            req = req['error']

            return req  # error message

    def PostCreatePayoff(self, request_sum, card):      # Создание вывода
        __URL = self.base_url + 'business/payoff/create'

        data = {
            "shopId": shop_id,
            "orderId": OrderGen(),
            "amount": request_sum,
            "service": "card_payoff",
            "subtract": 1,
            "walexport constTo": card
        }

        req = s.post(__URL, json=data, headers=HeaderGen(data))

        req = json.loads(req.text)
        try:
            req = req['data']['url']

            return req  #
        except TypeError:
            return req  # error message

    def PostInfoPayoff(self, order_id):     # Статус вывода
        __URL = self.base_url + 'business/payoff/info'

        data = {
            "shopId": shop_id,
            "orderId": order_id
        }

        req = s.post(__URL, json=data, headers=HeaderGen(data))

        req = json.loads(req.text)
        try:
            req = req['data']['url']

            return req  #
        except TypeError:
            req = req['error']

            return req  # error message

    def PostCheckWallet(self, card):      # Проверка действительности кошелька для вывода
        __URL = self.base_url + 'business/payoff/check-wallet'

        data = {
            "service": "card_payoff",
            "shopId": shop_id,
            "walletTo": card
        }

        req = s.post(__URL, json=data, headers=HeaderGen(data))

        req = json.loads(req.text)

        req = req['data']['status']

        return req


account = LavaPayment()
