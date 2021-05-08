from PyQt5.QtCore import pyqtSignal, QObject

import threading
from queue import Queue
import socket
import random
import math
# import time
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Util.Padding import unpad
from Crypto.Util.number import getPrime
from Crypto.Random import get_random_bytes
import ifaddr
import logging


PRIME_LENGTH = 256
MAX_LENGTH = PRIME_LENGTH * 2
PORT_DEF = 55778  # application port
logpath = "RX.log"


# возвращаемый аргумент x является мультипликативно обратным к a, b - модуль
def mult_inv(a, b):
    x, xx, y, yy = 1, 0, 0, 1
    while b:
        q = a // b
        a, b = b, a % b
        x, xx = xx, x - xx * q
        y, yy = yy, y - yy * q
    return x


# RSA-преобразование
def RSA(message, key, N):
    outputText = pow(message, key, N)
    return outputText


'''
Генерация параметров RSA

ВЫХОД:
1. открытый показатель e    (int)
2. закрытый показатель d    (int)
3. модуль n					(int)
'''


def generating_e_d():
    p = getPrime(PRIME_LENGTH, randfunc=get_random_bytes)
    q = getPrime(PRIME_LENGTH, randfunc=get_random_bytes)
    euler = (p - 1) * (q - 1)
    n = p * q
    while True:
        e = random.getrandbits(16)
        if (math.gcd(e, euler) == 1):
            break
    d = mult_inv(e, euler)
    while (d < 0):
        d = d + euler
    # print("e = " + str(e) + "\n")
    # print("d = " + str(d) + "\n")
    # print("n = " + str(n) + "\n")
    return e, d, n


'''
Генерация AES ключа и синхропосылки

ВХОД:
ВЫХОД:
1. ключ AES 	 			(bytes)
2. синхропосылка 			(bytes)
'''


def AES_generation():
    # random 32-byte key
    key = random.getrandbits(256)
    # print("Symmetric key (32-bytes): " + str(key) + "\n")

    # random 16-byte sync-pos
    sync_package = random.getrandbits(128)
    # print("Sync package (16-bytes): " + str(sync_package) + "\n")

    # зашифровываем файл(file_bytes) на симм.ключе key (результат в encd)
    key = key.to_bytes(32, byteorder='big')
    sync_package = sync_package.to_bytes(16, byteorder='big')

    return key, sync_package


'''
Зашифрование входного сообщения

ВХОД:
1. сообщение     			(bytes)
ВЫХОД:
1. зашифр.сообщ. 			(bytes)
'''


def AES_encrypt(file_bytes, k, iv):
    # key = k.to_bytes(32, byteorder='big')
    # sync_package = iv.to_bytes(16, byteorder='big')

    aes = AES.new(k, AES.MODE_CBC, iv)
    encd = aes.encrypt(pad(file_bytes, AES.block_size))

    return encd


'''
Зашифрование AES ключа и синхропосылки с помощью RSA

ВХОД:
1. ключ AES 				(bytes)
2. синхропосылка 			(bytes)
3. открытый показатель e 	(bytes)
4. модуль n 				(bytes)
ВЫХОД:
1. зашифр. ключ AES 		(int)
2. зашифр. синхропосылка 	(int)
'''


def RSA_encrypt(key, sync_package, e, n):
    # конвертируем в инту
    # e = int(e.decode())
    # n = int(n.decode())

    # обратно в инт
    key = int.from_bytes(key, byteorder='big')
    sync_package = int.from_bytes(sync_package, byteorder='big')

    # зашифровываем с помощью RSA AES ключ и синхропосылку
    rsa_key = RSA(key, e, n)
    rsa_sync = RSA(sync_package, e, n)

    return rsa_key, rsa_sync


'''
Расшифрование AES ключа и синхропосылки с помощью RSA

ВХОД:
1. зашифр. ключ AES 		(bytes)
2. зашифр. синхропосылка 	(bytes)
3. закрытый показатель e 	(bytes)
4. модуль n 				(bytes)
ВЫХОД:
1. расшифр. ключ AES 		(int)
2. расшифр. синхропосылка 	(int)
'''


def RSA_decrypt(key, sync, d, n):
    # в инту
    encr_key = int.from_bytes(key, 'big')
    encr_sync = int.from_bytes(sync, 'big')

    # расшифровывем ключ и синхропосылку
    decr_key = RSA(encr_key, d, n)
    decr_sync = RSA(encr_sync, d, n)

    return decr_key.to_bytes(32, 'big'), decr_sync.to_bytes(16, 'big')


'''
Расшифрование сообщения с помощью AES

ВХОД:
1. зашифр. сообщение 		(bytes)
2. расшифр. ключ AES 		(int)
3. расшифр. синхропосылка 	(int)
ВЫХОД:
1. расшифр. сообщение		(str)
'''


def AES_decrypt(encr_message, decr_key, decr_sync):
    # перевести в байты
    # decr_key = decr_key.to_bytes(32, byteorder='big')
    # decr_sync = decr_sync.to_bytes(16, byteorder='big')

    aes_2 = AES.new(decr_key, AES.MODE_CBC, decr_sync)
    decd = unpad(aes_2.decrypt(encr_message), AES.block_size)
    decd = decd.decode()
    return decd


class Header:  # header length is 9 bytes  #  0000[read][recvd][key_h][key_l]
    def __init__(self,
                 length: int,
                 flag_key_l: bool = False,
                 flag_key_h: bool = False,
                 flag_recvd: bool = False,
                 flag_read: bool = False,
                 id_message: int = 0):
        self.header_data = length.to_bytes(4, byteorder='big') \
                           + id_message.to_bytes(4, byteorder='big') \
                           + (flag_key_l + flag_key_h * 2 + flag_recvd * 4 + flag_read * 8).to_bytes(1, byteorder='big')

    @staticmethod
    def len_predef():
        return 9

    # |flags| = 1
    @staticmethod
    def parse_flags(flags: bytes):
        flag_key_l = flag_key_h = flag_recvd = flag_read = False
        f = int.from_bytes(flags, 'big')
        if f % 2:
            flag_key_l = True
        f //= 2
        if f % 2:
            flag_key_h = True
        f //= 2
        if f % 2:
            flag_recvd = True
        f //= 2
        if f % 2:
            flag_read = True
        return flag_key_l, flag_key_h, flag_recvd, flag_read

    @classmethod
    def from_raw(cls, raw_message: bytes):
        flag_key_l, flag_key_h, flag_recvd, flag_read = Header.parse_flags(raw_message[8:9])
        return cls(int.from_bytes(raw_message[:4], 'big'),
                   flag_key_l, flag_key_h, flag_recvd, flag_read,
                   int.from_bytes(raw_message[4:8], 'big'))

    def raw(self):
        return self.header_data

    def length(self):
        return int.from_bytes(self.header_data[:4], 'big')

    def id_message(self):
        return int.from_bytes(self.header_data[4:8], 'big')

    def flags(self):
        return self.header_data[8:9]


class Message:
    def __init__(self, header: Header, payload: bytes = None):
        self.header = header
        self.payload = payload
        self.id_message = header.id_message()

    @classmethod
    def message(cls, payload: bytes, id_message: int):
        return cls(header=Header(length=len(payload) + Header.len_predef(), id_message=id_message),
                   payload=payload)

    @classmethod
    def key_request(cls):
        print('key_request')
        return cls(header=Header(length=Header.len_predef(), flag_key_l=True))

    # |e| = 2 bytes, |n| = 512 bytes
    @classmethod
    def key_reply_rsa(cls, e: int, n: int):
        return cls(header=Header(length=MAX_LENGTH + 2 + Header.len_predef(), flag_key_h=True),
                   payload=e.to_bytes(2, byteorder='big') + n.to_bytes(512, byteorder='big'))

    @classmethod
    def key_reply_aes(cls, k: bytes, iv: bytes):
        return cls(header=Header(length=MAX_LENGTH * 2 + Header.len_predef(), flag_key_l=True, flag_key_h=True),
                   payload=k + iv)

    @classmethod
    def state_received(cls, id_message: int):
        return cls(header=Header(length=Header.len_predef(), id_message=id_message, flag_recvd=True))

    @classmethod
    def state_read(cls, id_message: int):
        return cls(header=Header(length=Header.len_predef(), id_message=id_message, flag_read=True))

    def raw(self):
        if self.payload is None:
            return self.header.raw()
        return self.header.raw() + self.payload


class network(QObject):
    received = pyqtSignal(str, str)  # str is the received message
    # int for the next three signals is message id from the send function
    undelivered = pyqtSignal(int, str)  # emit when timeout is off and the message isn't delivered
    delivered = pyqtSignal(int, str)  # emit when delivered
    read = pyqtSignal(int, str)  # emit when read
    client_connected = pyqtSignal(str)  # str - ip
    connection_established = pyqtSignal(bool, str)  # true/false, ip
    exit_event = threading.Event()

    logger = logging.getLogger('RX')


    def __init__(self):
        super(network, self).__init__()

        self.restricted_ip = ['127.0.0.1']

        self.queue_tx = Queue()  # queue of (id_client, message) for transmission
        self.queue_rx = Queue()  # queue of (id_client, message) received
        self.messages_log = []  # list of ('<T/R>', <ip>, <message>) - all users' msgs. T-transmission, R - receive
        # self.restore_msg_log(self.messages_log)  # TODO: update from offline cache on init

        self.clients_states = []  # 'ip' # all ever connected clients' IPs
        self.clients_connections = {}  # 'ip': connection
        self.clients_keys = {}  # 'ip': ((key, iv), (d, n)) # (d, n) - private key, maybe None if not needed
        self.listeners = []  # array of sockets

        self.logger.setLevel(logging.INFO)
        ch = logging.FileHandler(logpath)
        self.logger.addHandler(ch)

        # Init sockets
        adapters = ifaddr.get_adapters()

        for adapter in adapters:
            for ip_ in adapter.ips:
                if isinstance(ip_.ip, str):
                    s = socket.socket()
                    try:
                        s.bind((ip_.ip, PORT_DEF))
                    except Exception as e:
                        continue
                    print('Listening on ' + ip_.ip + ':' + str(PORT_DEF))
                    self.listeners.append(s)
                    self.restricted_ip.append(ip_.ip)
                    threading.Thread(target=self.worker_main_listener, args=(s,)).start()

        self.thread_sender = threading.Thread(target=self.worker_sender).start()

    def __del__(self):
        self.exit_event.set()

        for s in self.clients_connections:
            try:
                s.close()
            except:
                pass
        for s in self.listeners:
            try:
                s.close()
            except:
                pass

    # def restore_msg_log(self, log: list):
    #     # TODO
    #     pass

    def worker_sender(self):
        while True:
            if self.exit_event.is_set():
                break

            addr, msg = self.queue_tx.get()  # this awaits until an item is available

            try:
                conn = self.clients_connections[addr[0]]
            except KeyError:
                self.signal_undelivered(msg.header.id_message(), addr[0])
                continue

            conn.send(msg.raw())
            if msg.header.id_message():
                self.signal_message_sent(msg.header.id_message())

    def worker_main_listener(self, socket_):
        socket_.listen(10)
        while True:
            if self.exit_event.is_set():
                break

            connection, addr = socket_.accept()
            self.clients_connections[addr[0]] = connection
            threading.Thread(target=self.worker_client_listener, args=(addr, connection)).start()
            print('Inbound connection: ' + addr[0])
            self.signal_client_connected(addr[0])

    def worker_client_listener(self, address: (str, int), connection_ = None):
        if connection_ is None:
            s = socket.socket()
            try:
                s.connect(address)
            except Exception as e:
                print('Error: ' + str(e))
                s.close()
                self.connection_established.emit(False, address[0])
                return
            self.clients_connections[address[0]] = s
            connection = self.clients_connections[address[0]]

            if address[0] not in self.clients_states:
                self.clients_states.append(address[0])

            self.init_session_key(address)  # TODO мб еще когда-то запрашивать новый сеансовый ключ

            self.connection_established.emit(True, address[0])
        else:
            connection = connection_


        while True:
            if self.exit_event.is_set():
                break

            try:
                header_raw = connection.recv(Header.len_predef())
            except:
                break
            header = Header.from_raw(header_raw)
            flag_key_l, flag_key_h, flag_recvd, flag_read = header.parse_flags(header.flags())

            print('recvd vvv')
            print(header.length())
            print(header.header_data)
            print('^^^')

            if flag_key_l and not flag_key_h:
                self.got_rsa_req(address)
                continue
            elif not flag_key_l and flag_key_h:
                data = connection.recv(header.length() - Header.len_predef())
                if not data:
                    break
                self.got_rsa_public_key(address, data[:2], data[2:514])
                continue
            elif flag_key_l and flag_key_h:
                data = connection.recv(header.length() - Header.len_predef())
                self.got_session_key(address, data[:512], data[512:])
                continue
            elif flag_recvd:
                self.signal_delivered(header.id_message(), address[0])
                continue
            elif flag_read:
                self.signal_read(header.id_message(), address[0])
                continue

            data = connection.recv(header.length() - Header.len_predef())
            if not data:
                break
            key, iv = (self.clients_keys[address[0]])[0]
            data_decrypted = AES_decrypt(data, key, iv)

            print(data)
            print(data_decrypted)

            message = Message(header, data_decrypted)
            self.send_received(message, address)  # подтверждаем принятие
            self.queue_rx.put((address, message))
            self.logger.info(address[0] + " " + data_decrypted)
            self.messages_log.append(('R', address[0], message))

        connection.close()
        self.clients_connections.pop(address[0])

    def got_rsa_req(self, address: (str, int)):
        # generate RSA parameters
        e, d, n = generating_e_d()

        self.clients_keys[address[0]] = (None, (d, n))

        # send public key =(e, n):
        msg_pk = Message.key_reply_rsa(e, n)
        self.send_any_message(msg_pk, address)

    def got_rsa_public_key(self, address: (str, int), e: bytes, n: bytes):
        # generate, save and send encrypted session key (session_key = (key, iv))
        key, iv = AES_generation()
        key_encr, iv_encr = RSA_encrypt(key, iv, int.from_bytes(e, 'big'), int.from_bytes(n, 'big'))
        self.clients_keys[address[0]] = ((key, iv), None)
        msg = Message.key_reply_aes(key_encr.to_bytes(MAX_LENGTH, 'big'),
                                    iv_encr.to_bytes(MAX_LENGTH, 'big'))
        self.send_any_message(msg, address)

    def got_session_key(self, address: (str, int), key_encr, iv_encr):
        d, n = (self.clients_keys[address[0]])[1]
        key, iv = RSA_decrypt(key_encr, iv_encr, d, n)
        self.clients_keys[address[0]] = ((key, iv), None)

    def send_any_message(self, message: Message, address: (str, int)):
        print('sent vvv')
        print(message.header.header_data)
        print(message.header.length())
        print('^^^')
        self.queue_tx.put((address, message))

    def init_session_key(self, address: (str, int)):
        self.send_any_message(Message.key_request(), address)

    # INTERFACE
    def signal_delivered(self, id_message: int, ip: str):
        # отправить на фронтенд сигнал, что сообщение получено
        self.delivered.emit(id_message, ip)

    # INTERFACE
    def signal_read(self, id_message: int, ip: str):
        # отправить на фронтенд сигнал, что сообщение прочитано
        self.read.emit(id_message, ip)

    # INTERFACE
    def signal_message_sent(self, id_message: int):
        # TODO: отправить на фронтенд сигнал, что сообщение успешно отправилось
        pass

    # INTERFACE
    def signal_client_connected(self, ip: str):
        # отправить на фронтенд сигнал, что клиент подключился, если он не подключался ранее
        if ip not in self.clients_states:
            self.client_connected.emit(ip)
            self.clients_states.append(ip)

    # INTERFACE
    def signal_undelivered(self, id_message: int, ip: str):
        # отправить на фронтенд сигнал, что сообщение не доставлено
        self.undelivered.emit(id_message, ip)

    # INTERFACE
    def send_received(self, message: Message, address: (str, int)):
        self.received.emit(message.payload, address[0])
        msg = Message.state_received(message.id_message)
        self.send_any_message(msg, address)

    # INTERFACE METHOD
    # Отправить "сообщение ID прочитано"
    def send_read(self, id_message: int, ip: str):
        msg = Message.state_read(id_message)
        self.send_any_message(msg, (ip, PORT_DEF))

    # INTERFACE METHOD
    # Отправка сообщения.
    # message  полезная нагрузка в формате bytes
    def send_message(self, id_message: int, message: str, ip: str):
        key, iv = (self.clients_keys[ip])[0]
        msg = Message.message(AES_encrypt(message.encode(), key, iv),
                              id_message)
        self.send_any_message(msg, (ip, PORT_DEF))
        self.messages_log.append(('T', ip, message.encode()))

    # INTERFACE METHOD
    def connect_to(self, ip: str):
        if ip in self.restricted_ip:
            return False

        threading.Thread(target=self.worker_client_listener, args=((ip, PORT_DEF), None)).start()

        return True
