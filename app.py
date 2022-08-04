import asyncio
import aiohttp
import json
from aiohttp import web

import aiohttp_jinja2
import jinja2

URLS = ['http://whatismyip.akamai.com/', 'https://api.ipify.org/', 'https://icanhazip.com/']


def write_to_json(url: str, ip: str):
    template = {
        "URL": url,
        "IP": ip.strip()
    }

    try:
        with open("data.json", encoding='utf-8') as file:
            data = json.load(file)
    except:
        with open("data.json", 'w', encoding='utf-8') as file:
            json.dump([], file, indent=4, ensure_ascii=False)
        with open("data.json", encoding='utf-8') as file:
            data = json.load(file)

    data.append(template)

    with open('data.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


async def get(session: aiohttp.ClientSession, url: str):
    async with session.get(url, ssl=False) as response:
        ip = await response.text()
        write_to_json(url, ip)


async def main(urls: list):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            tasks.append(get(session=session, url=url))
        htmls = await asyncio.gather(*tasks)
        return htmls


@aiohttp_jinja2.template('ips.html')
async def get_ips(request):
    with open("data.json", encoding='utf-8') as file:
        data = json.load(file)

    return {'data': data}


if __name__ == '__main__':
    app = web.Application()
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('templates'))
    app.add_routes([web.get('', get_ips)])

    asyncio.run(main(URLS))

    web.run_app(app)
