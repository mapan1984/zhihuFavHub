#!/usr/bin/env python
import os
import json
import requests
import argparse
import http.cookiejar
from urllib import parse, request, error

from pyquery import PyQuery as pq


base_path = os.path.dirname(os.path.abspath(__file__))

cookie = http.cookiejar.MozillaCookieJar(os.path.join(base_path, 'cookie.txt'))
try:
    cookie.load()
except IOError:
    print('Load Cookie failed!')
cookieProcessor = request.HTTPCookieProcessor(cookie)
opener = request.build_opener(cookieProcessor)
request.install_opener(opener)


ses = requests.Session()
ses.coookies = cookie

add_ans_url = 'https://www.zhihu.com/collection/add'
add_post_url = 'https://www.zhihu.com/api/v4/favlists/{collection_id}/items'

follow_url = 'https://www.zhihu.com/collection/follow'

headers = {
    # 'HOST': 'www.zhihu.com',
    # 'Origin': 'https://www.zhihu.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
}


def get_collection_url(col_id: str) -> str:
    """ 生成收藏夹页面路由
    Args:
        col_id: 收藏夹id
    """
    col_url = f'https://www.zhihu.com/collection/{col_id}'
    yield col_url
    page = 2
    while True:
        query = {'page': page}
        query_col_url = col_url + '?' + parse.urlencode(query)
        yield query_col_url
        if page >= 2:
            break
        page += 1


def get_collection_page(col_url: str) -> str:
    """ 获取收藏夹页面
    Args:
        col_url: 收藏夹url
    """
    req = request.Request(col_url, headers=headers)
    try:
        response = request.urlopen(req)
    except error.HTTPError as err:
        if err.code == 404:
            print('Collection page not found!')
        raise
    else:
        html = response.read()
        response.close()
        return html.decode('utf-8')


def get_xsrf(html: str) -> str:
    """ 获取`_xsrf`
    Args:
        html: 收藏夹页面
    """
    d = pq(html)
    bin_xsrf = d('input[name=_xsrf]').attr('value')
    # print(bin_xsrf)
    xsrf = ''
    if bin_xsrf is None:
        return xsrf
    for i in range(0, len(bin_xsrf), 2):
        xsrf += chr(int(bin_xsrf[i:i + 2], base=16))
    # print(xsrf)
    return bin_xsrf


def get_answer_ids(html: str) -> str:
    """ 获取回答的id
    Args:
        html: 收藏夹页面
    """
    d = pq(html)
    ans = d('.zm-item-answer')
    for a in ans.items():
        ans_id = a.attr['data-aid']
        # print(ans_id)
        yield ans_id


def get_post_ids(html: str) -> str:
    """ 获取文章的id
    Args:
        html: 收藏夹页面
    """
    d = pq(html)
    post = d('meta[itemprop=post-url-token]')
    for p in post.items():
        post_id = p.attr['content']
        # print(ans_id)
        yield post_id


def add_answer(ans_id: str, fav_id: str, xsrf: str):
    """ 将一个回答加入收藏夹
    Args:
        ans_id: 回答id
        fav_id: 目的收藏夹favlist_id(用户自建)
        xsrf:
    """
    data = parse.urlencode({
        'answer_id': ans_id,
        'favlist_id': fav_id,
        '_xsrf': xsrf,
    }).encode('ascii')
    req = request.Request(add_ans_url, data, headers)
    try:
        response = request.urlopen(req)
    except error.HTTPError as err:
        if err.code == 403:
            print('Forbidden, check you cookie.txt')
        raise
    else:
        # print(response.info())
        res_body = response.read()
        response.close()
        j = json.loads(res_body.decode('utf-8'))
        print(j)
        return j['r'] == 0


def add_post(content_id: str, collection_id: str, xsrf: str):
    """ 将一个回答加入收藏夹
    Args:
        content_id: 文章id
        collection_id: 目的收藏夹id(用户自建)
    """
    # data = json.dumps({
    #     'content_id': content_id,
    #     'content_type': 'article',
    # }).encode('utf-8')
    j = {
        'content_id': content_id,
        'content_type': 'article',
    }
    post_url = f'https://zhuanlan.zhihu.com/p/{content_id}'
    # headers.update({
    #     # 'x-xsrftoken': xsrf,
    #     'Origin': 'https://zhuanlan.zhihu.com',
    #     'Referer': 'https://zhuanlan.zhihu.com/p/{content_id}',
    #     'Content-Type': 'application/json',
    # })

    add_url = add_post_url.format(collection_id=collection_id)

    print(post_url)
    r = ses.get(post_url, headers=headers)
    print(r.status_code)
    r = ses.options(add_url, headers=headers)
    print(r.status_code)
    headers.update({
        'Origin': 'https://zhuanlan.zhihu.com',
        'Referer': post_url,
        'x-requested-with': 'Fetch',
        'x-udid': 'ADBgeQReiA2PTrIr-D8HgJbQc2Z8W_HkbDM=',
        'x-xsrftoken': '96a13e18-104b-4ed1-b6d9-fcd6ea3d79e9'
    })
    r = ses.post(add_url, headers=headers, json=j)
    print(r.json())

    # url = add_post_url.format(collection_id=collection_id)
    # req = request.Request(url, data, headers)
    # try:
    #     response = request.urlopen(req)
    # except error.HTTPError as err:
    #     if err.code == 403:
    #         print('Forbidden, check you cookie.txt')
    #     print(url)
    #     print(req.get_method())
    #     print(err.headers)
    #     print(err.errno)
    #     print(err.reason)
    #     raise
    # else:
    #     # print(response.info())
    #     res_body = response.read()
    #     response.close()
    #     j = json.loads(res_body.decode('utf-8'))
    #     print(j)
    #     return j['r'] == 0


def merge_collection(res_col_id: str, des_fav_id: str, des_col_id: str):
    """ 合并一个收藏夹内容到目的收藏夹
    Args:
        res_col_id: 源收藏夹id
        des_fav_id: 目的收藏夹favlist_idid(用户自建)
        des_col_id: 目的收藏夹id(用户自建)
    """
    print(f'get collection page {res_col_id}...')
    for col_url in get_collection_url(res_col_id):
        print(col_url)
        colhtml = get_collection_page(col_url)
        xsrf = get_xsrf(colhtml)

        # headers.update({
        #     'Referer': col_url
        # })
#
        # for post_id in get_post_ids(colhtml):
        #     add_post(post_id, des_col_id, xsrf)

        con = 0
        for ans_id in get_answer_ids(colhtml):
            ok = add_answer(ans_id, des_fav_id, xsrf)
            if ok:
                con = 0
            else:
                con += 1
            if con >= 2:
                break
        if con >= 2:
            break


def merge_all_collections():
    """合并所有收藏夹"""
    for res_col_id in collection_ids:
        try:
            merge_collection(res_col_id, favlist_id, collection_id)
        except (KeyboardInterrupt, SystemExit):
            print('stop')
            # save cookie
            break


def follow(favlist_id):
    """关注一个收藏夹"""
    data = parse.urlencode({
        'favlist_id': favlist_id
    }).encode('ascii')
    req = request.Request(follow_url, data, headers)
    try:
        response = request.urlopen(req)
    except error.HTTPError as err:
        if err.code == 403:
            print('Forbidden, check you cookie.txt')
        raise
    else:
        # print(response.info())
        res_body = response.read()
        response.close()
        j = json.loads(res_body.decode('utf-8'))
        print(j)
        return j['r'] == 0


def follow_all_collections():
    """关注所有收藏夹"""
    for col_id in collection_ids:
        print(f'get page {col_id}')
        col_url = f'https://www.zhihu.com/collection/{col_id}'
        html = get_collection_page(col_url)
        headers.update({
            'Referer': col_url,
            'x-xsrftoken': get_xsrf(html),
        })
        d = pq(html)
        favlist_id = d('.ga-follow-fav').attr('id')[3:]
        print(favlist_id)
        follow(favlist_id)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--merge", action="store_true", default=True,
                        help="merge all collections to favlist")
    parser.add_argument("-f", "--follow", action="store_true", default=False,
                        help="follow all collections")
    parser.add_argument("-c", "--config", type=str, default='config.json',
                        help="select a config file")
    args = parser.parse_args()

    if args.config:
        with open(args.config, 'r', encoding='utf-8') as fd:
            config = json.load(fd)
        favlist_id = config['favlist_id']
        collection_id = config['collection_id']
        collection_ids = config['collection_ids']

    if args.follow:
        follow_all_collections()
    elif args.merge:
        merge_all_collections()

