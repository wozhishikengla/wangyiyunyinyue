import base64
import binascii
import json
import multiprocessing
import random
import threading
import time
import pymongo
import requests
import  setting
from Crypto.Cipher import AES
from bs4 import BeautifulSoup


class Download():
    def __init__(self):
        self.headers = {
            'Accept':
                '*/*',
            'Accept-Encoding':
                'gzip, deflate, br',
            'Accept-Language':
                'zh-CN,zh;q=0.9',
            'Connection':
                'keep-alive',
            'Content-Length':
                '484',
            'Content-Type':
                'application/x-www-form-urlencoded',
            'Cookie':
                '_iuqxldmzr_=32; _ntes_nnid=66d3ea42ca8ec7e02ccfdb9d7d16b642,1538552797279; _ntes_nuid=66d3ea42ca8ec7e02ccfdb9d7d16b642; WM_TID=zATDzT4gvhFERVVRVRM9lQl2tDXkZIrs; __utmc=94650624; __utmz=94650624.1546913354.3.3.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; WM_NI=DyA0rlZ8xWeCPFYBDS4%2F45FrXroEsZY9TU%2Ft4LVCyDc2g4wZkthTzwbhWEPhO%2B8UVEQ6inn79Mk8I6KC5nOzqnriRHAJK4uxf2w4iOz%2FNMngr1Zxo91D3sdld7oHpXe4cFI%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6ee8ab139ed8996add654f3eb8ba3c85a828e9abab86d87edabb4bc4d8c899c88b52af0fea7c3b92a88a78fd1f1689ae8b8b8e849949a97a3c759f8f1fcd6c57a9caea1a6f2529be79cb6ae80f8949aa4fc50a1eea9d5f652a9aca8b5f97da2b899a6d3648df5f8b6d54f93eaa78fed3dfb93a5d9cc3e899dfb8fce72b3b2be8ad144839685d5f874a6eeb9d5ec45baf182aeed6db2ef9699ee33f39cfd94e768a8e9a1a9f354a7ecada7cc37e2a3; __utma=94650624.636335447.1546821878.1546913354.1546916714.4; JSESSIONID-WYYY=dXsIK%2BfuupsDeW4%2FQ8ixp6Augz6tYOUOj60iNK%5CerA%2BqrbqxE804CeZ%2F5z2H5gryt3bSeP1uliOK7GC%2F5IIYzGWDpq0lu%2FxYb%2FoEaq%2BGcPkm2q86lANrCI6Ok2OIFefrYnXsRFH7kOK%2F%2BU28pIzgUMYXm0%2B4SMn%2Bia4wu5n%2Fs0vNoDfi%3A1546918633661; __utmb=94650624.3.10.1546916714',
            'Host':
                'music.163.com',
            'Origin':
                'https://music.163.com',
            'Referer':
                'https://music.163.com/song?id={ids}'.format(ids=ids),
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36}'
        }

    def songlist(self):
        url = 'https://music.163.com/discover/toplist?id=3778678'
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'lxml')
        ul = soup.find('ul', class_="f-hide")
        idlist = []
        for li in ul.find_all('li'):
            li = li.find('a')
            ids = li.get('href')
            ids = ids[9:]
            name = li.get_text()
            idlist.append((ids, name))
        return idlist

    def get_comment(self, ids, offest, semlock, name):
        if offest == 0:
            data = '{"rid":"R_SO_4_%s","offset":"0","total":"ture","limit":"20","csrf_token":""}' % ids
        else:
            data = '{"rid":"R_SO_4_%s","offset":"%d","total":"ture","limit":"20","csrf_token":""}' % (
                ids, offest)
        data = AES_encrypt.params_get(data)
        url = 'https://music.163.com/weapi/v1/resource/comments/R_SO_4_{}?csrf_token='.format(
            ids)
        response = requests.post(url, headers=self.headers, data=data)
        if response.status_code == 200:
            get_data = json.loads(response.text)
            if offest == 0:
                hotcomments = get_data['hotComments']
                hotcommentslist = []
                for comment in hotcomments:
                    userid = comment['user']['userId']
                    nickname = comment['user']['nickname']
                    img_url = comment['user']['avatarUrl']
                    time1 = eval(str(comment['time'])[:10])
                    timeArray = time.localtime(time1)
                    time1 = time.strftime('%Y-%m-%d %H:%M:%S', timeArray)
                    content = comment['content'].replace('\n', '')
                    likedCount = comment['likedCount']
                    hotcomment1 = {
                        'userid': userid,
                        'nickname': nickname,
                        'img_url': img_url,
                        'time1': time1,
                        'content': content,
                        'likedCount': likedCount
                    }
                    hotcommentslist.append(hotcomment1)
                comments = get_data['comments']
                commentslist = []
                for comment in comments:
                    userid = comment['user']['userId']
                    nickname = comment['user']['nickname']
                    img_url = comment['user']['avatarUrl']
                    time1 = eval(str(comment['time'])[:10])
                    timeArray = time.localtime(time1)
                    time1 = time.strftime('%Y-%m-%d %H:%M:%S', timeArray)
                    content = comment['content'].replace('\n', '')
                    likedCount = comment['likedCount']
                    comment1 = {
                        'userid': userid,
                        'nickname': nickname,
                        'img_url': img_url,
                        'time1': time1,
                        'content': content,
                        'likedCount': likedCount
                    }
                    commentslist.append(comment1)
                save_to_mongo(name, hotcommentslist)
                save_to_mongo(name, commentslist)

            else:
                comments = get_data['comments']
                commentslist = []
                for comment in comments:
                    userid = comment['user']['userId']
                    nickname = comment['user']['nickname']
                    img_url = comment['user']['avatarUrl']
                    time1 = eval(str(comment['time'])[:10])
                    timeArray = time.localtime(time1)
                    time1 = time.strftime('%Y-%m-%d %H:%M:%S', timeArray)
                    content = comment['content'].replace('\n', '')
                    likedCount = comment['likedCount']
                    comment1 = {
                        'userid': userid,
                        'nickname': nickname,
                        'img_url': img_url,
                        'time1': time1,
                        'content': content,
                        'likedCount': likedCount
                    }
                    commentslist.append(comment1)
                # print(commentslist)
                save_to_mongo(name, commentslist)
            print(threading.get_ident())
            semlock.release()

    def download_lyric(self, ids, name, semlock):
        print('开始下载' + name + '.txt')
        url = 'https://music.163.com/weapi/song/lyric?csrf_token='
        data = '{"id":"%s","lv":-1,"tv":-1,"csrf_token":""}' % ids
        data = AES_encrypt.params_get(data)
        response = requests.post(url, headers=self.headers, data=data)
        if response.status_code == 200:
            get_data = json.loads(response.text)
            data = get_data['lrc']['lyric']
            filename = './Music/{name}.txt'.format(name=name)
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(data.encode().decode('utf-8'))
        print('下载完成' + name + '.txt')
        semlock.release()

    def download_music(self, ids, name, semlock):
        print('开始下载' + name + '.mp3')
        url = 'https://music.163.com/weapi/song/enhance/player/url?csrf_token='
        data = "{'ids': ['%s'], 'br': '12800', 'csrf_token': ''}" % ids
        data = AES_encrypt.params_get(data)
        response = requests.post(url, headers=self.headers, data=data)
        if response.status_code == 200:
            get_data = json.loads(response.text)
            url = get_data['data'][0]['url']
        headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            filename = './Music/{name}.mp3'.format(name=name)
            with open(filename, 'wb') as f:
                f.write(response.content)
        print('下载完成' + name + '.mp3')
        semlock.release()

    def save_to_mongo(self, name, item):
        client = pymongo.MongoClient(setting.HOST,setting.PROT)
        db = client[setting.CLIENT]
        p = db[name]
        p.insert(item)

    def get_number(self, ids):
        data = '{"rid":"R_SO_4_%s","offset":"0","total":"ture","limit":"20","csrf_token":""}' % ids
        data = AES_encrypt.params_get(data)
        url = 'https://music.163.com/weapi/v1/resource/comments/R_SO_4_{}?csrf_token='.format(
            ids)
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            get_data = json.loads(response.text)
            total = get_data['total']
            if total % 20 != 0:
                number = total // 20 + 1
            else:
                number = total // 20
        return number


class AES_encrypt():
    def __init__(self):
        self.pub_key = "010001"
        self.modulus = "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7"
        self.key = "0CoJUm6Qyw8W8jud"

    def aes_jiami(self, text, key):
        if type(text) == dict:
            text = json.dumps(text)
        if type(text) != str:
            text = text.decode('utf-8')
        pad = 16 - len(text) % 16
        if pad != 0:
            text = text + pad * chr(pad)  # It shoud be 16-x not
        if type(key) == str:
            key = key.encode()
        if type(text) == str:
            text = text.encode()
        cipher = AES.new(key, AES.MODE_CBC, b"0102030405060708")
        msg = cipher.encrypt(text)
        msg = base64.b64encode(msg)
        return msg

    def rsa_encrypt(self, ran_16, pub_key, modulus):
        text = ran_16[::-1]  # 明文处理，反序并hex编码
        if type(text) == str:
            text = text.encode()
        rsa = int(binascii.hexlify(text), 16) ** int(pub_key, 16) % int(modulus,
                                                                        16)
        return format(rsa, 'x').zfill(256)

    def random_16(self):
        return bytes(''.join(random.sample('1234567890DeepDarkFantasy', 16)),
                     'utf-8')

    def params_get(self, text):
        ran_16 = random_16()
        params = AES_jiami(text, self.key)
        params = AES_jiami(params, ran_16)
        encSecKey = rsa_encrypt(ran_16, self.pub_key, self.modulus)
        return {'params': params.decode(), 'encSecKey': encSecKey}


def thread(down, ids, name):
    number = get_number(ids)
    list1 = []
    semlock = threading.BoundedSemaphore(10)
    semlock.acquire()
    t1 = threading.Thread(target=down.download_music, args=(ids, name, semlock))
    t1.start()
    semlock.acquire()
    t2 = threading.Thread(target=down.download_lyric, args=(ids, name, semlock))
    t2.start()
    for i in range(number + 1):
        semlock.acquire()
        t = threading.Thread(
            target=down.get_comment, args=(ids, i * 20, semlock, name))
        list1.append(t)
        t.start()
        print(threading.active_count())


def main():
    down = Download()
    pool = multiprocessing.Pool(processes=2)
    list_of_song = down.songlist()
    for song in list_of_song:
        ids = song[0]
        name = song[1]
        thread(ids, name)
        pool.apply_async(thread, (down, ids, name))
    pool.close()
    pool.join()

if __name__ == "__main__":
    main()