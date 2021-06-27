# -*- coding: utf-8 -*-
# Created by calle on 2021/6/13 10:55
# Copyright (c) 2021 calle. All rights reserved.


import logging
import time
import urllib
import bs4
import requests

from concurrent.futures import ThreadPoolExecutor

# logging.disable(logging.INFO)
logging.disable(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG, format=" %(asctime)s - %(levelname)s - %(message)s")


def get_page_url(url):
	logging.info('Start getting page url')
	result = []
	url_netloc = urllib.parse.urlparse(main_page).netloc
	res = requests.get(url)
	res.raise_for_status()
	res.encoding = "utf-8"
	page_soup = bs4.BeautifulSoup(res.text, features='lxml')
	div_content = page_soup.select('div [id="list"]')
	div_list = div_content[0].contents[1].contents
	div_list = div_list[1::2]

	name = page_soup.select('h1')[0].text

	for content in div_list:
		div_content = {}
		try:
			if len(content.contents) > 1:
				href = content.contents[1].attrs['href']
				div_content['href'] = url_netloc + href
				div_content['title'] = content.contents[1].text
				logging.debug(f'章节： {content.contents[1].text}')
			else:
				div_content['href'] = None
				div_content['title'] = content.text
				logging.debug(f'卷  ： {content.text}')
		except Exception as e:
			logging.error(f'get url error {e}')

		result.append(div_content)

	logging.info('Page url ready')
	return (result, name)


def get_page_content(url):
	url = url['href']
	if not url:
		return ''
	else:
		url = 'http://' + url

	res = requests.get(url)
	res.raise_for_status()
	page_soup = bs4.BeautifulSoup(res.text, features='lxml')
	div_content = page_soup.select('div [id="content"]')[0].text
	div_content = div_content.replace('　　', '\n')
	# div_content = div_content.replace('\r\n\t\t\t\t\n', '\n') + '\n'

	return div_content


def save_text():
	pass


if __name__ == '__main__':

	# main_page = "http://www.kanshuw.com/23/23953/"
	main_page = "https://www.23hh.com/book/6/6899/"
	# main_page = 'https://www.tianxiabachang.cn/42_42909/'
	chapter_page_list, name = get_page_url(main_page)
	max_workers = 20
	executor = ThreadPoolExecutor(max_workers)
	# all_task = [executor.submit(get_page_content, (url)) for url in chapter_page_list]

	count = 0
	begin = time.time()
	with open(name + '.txt', 'w', encoding='utf-8') as file:
		for data in executor.map(get_page_content, chapter_page_list):
			title = chapter_page_list[count]['title']
			text = title + data
			count += 1
			try:
				file.write(text)
				logging.info(f'write {title}')
			except Exception as e:
				logging.error(f'write file error:{e}')

	stop = time.time()

	logging.info(f'time {stop - begin}')
