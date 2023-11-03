import hashlib
import hmac
import json
import random
import string
import requests


class LavaPayment:
    def __init__(self, shop_id: str, secret_key: str):
        """
        Инициализирует объект LavaPayment.

        :param shop_id: id Магазина
        :type shop_id: str
        :param secret_key: Ключ аккаунта
        :type secret_key: str
        """
        self.shop_id = shop_id
        self.secret_key = secret_key
        self.base_url = 'https://api.lava.ru/'

        self.s = requests.session()

    @staticmethod
    def OrderGen():
        """
        Генерирует уникальный идентификатор для запросов.

        :return: Уникальный идентификатор
        :rtype: str
        """
        random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))

        return random_string

    def HeaderGen(self, data):
        """
        Генерирует заголовок для запроса.

        :param data: Данные запроса
        :type data: dict
        :return: Заголовок запроса
        :rtype: dict
        """
        json_str = json.dumps(data).encode()

        sign = hmac.new(bytes(self.secret_key, 'UTF-8'), json_str, hashlib.sha256).hexdigest()

        header = {
            'Signature': sign,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        return header

    def PostAvailableTariffs(self):
        """
        Отправляет запрос для получения доступных тарифов.

        :return: Ответ сервера
        :rtype: dict
        """
        __URL = self.base_url + 'business/invoice/get-available-tariffs'

        data = {
            'shopId': self.shop_id
        }

        req = self.s.post(__URL, json=data, headers=self.HeaderGen(data))

        req = json.loads(req.text)

        return req

    def PostCreateInvoice(self, request_sum):
        """
        Создает платеж и возвращает URL для оплаты.

        :param request_sum: Сумма платежа
        :type request_sum: float
        :return: URL для оплаты и уникальный идентификатор заказа
        :rtype: list
        """
        __URL = self.base_url + 'business/invoice/create'

        gen_order_id = self.OrderGen()

        data = {
            "shopId": self.shop_id,
            "sum": request_sum,
            "orderId": gen_order_id,
            "successUrl": "Ссылка на вашего бота",
            "failUrl": "Ссылка на вашего бота",
            "expire": 10,  # Время жизни ссылки
            "comment": "Пополнение баланса",
            "includeService": ["card", "sbp", "qiwi"]  # Доступные методы
        }

        req = self.s.post(__URL, json=data, headers=self.HeaderGen(data))

        req = json.loads(req.text)
        req = req['data']['url']

        return [req, gen_order_id]

    def PostStatusInvoice(self, order_id):
        """
        Проверяет статус платежа по его идентификатору.

        :param order_id: Идентификатор заказа
        :type order_id: str
        :return: Статус платежа
        :rtype: str
        """
        __URL = self.base_url + 'business/invoice/status'

        data = {
            'orderId': order_id,
            'shopId': self.shop_id
        }

        req = self.s.post(__URL, json=data, headers=self.HeaderGen(data)).text

        req = json.loads(req)
        try:
            req = req['data']['status']

            return req  # success, created
        except TypeError:
            req = req['error']

            return req  # error message

    def PostCreatePayoff(self, request_sum, card):
        """
        Создает запрос на вывод средств на указанную карту.

        :param request_sum: Сумма вывода
        :type request_sum: float
        :param card: Номер карты для вывода средств
        :type card: str
        :return: URL для подтверждения вывода или сообщение об ошибке
        :rtype: str
        """
        __URL = self.base_url + 'business/payoff/create'

        data = {
            "shopId": self.shop_id,
            "orderId": self.OrderGen(),
            "amount": request_sum,
            "service": "card_payoff",
            "subtract": 1,
            "walexport constTo": card
        }

        req = self.s.post(__URL, json=data, headers=self.HeaderGen(data))

        req = json.loads(req.text)
        try:
            req = req['data']['url']

            return req  #
        except TypeError:
            return req  # error message

    def PostInfoPayoff(self, order_id):
        """
        Проверяет статус вывода средств по его идентификатору.

        :param order_id: Идентификатор вывода средств
        :type order_id: str
        :return: Информация о выводе или сообщение об ошибке
        :rtype: str
        """
        __URL = self.base_url + 'business/payoff/info'

        data = {
            "shopId": self.shop_id,
            "orderId": order_id
        }

        req = self.s.post(__URL, json=data, headers=self.HeaderGen(data))

        req = json.loads(req.text)
        try:
            req = req['data']['url']

            return req  #
        except TypeError:
            req = req['error']

            return req  # error message

    def PostCheckWallet(self, card):
        """
        Проверяет действительность кошелька для вывода средств.

        :param card: Номер карты для проверки
        :type card: str
        :return: Статус проверки
        :rtype: str
        """
        __URL = self.base_url + 'business/payoff/check-wallet'

        data = {
            "service": "card_payoff",
            "shopId": self.shop_id,
            "walletTo": card
        }

        req = self.s.post(__URL, json=data, headers=self.HeaderGen(data))

        req = json.loads(req.text)

        req = req['data']['status']

        return req
