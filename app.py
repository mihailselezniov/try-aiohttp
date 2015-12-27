import os, asyncio, jinja2, aiohttp_jinja2, pickle
from aiohttp import web


async def formshandler(request):
    with open('data.pickle', 'rb') as f: data = pickle.load(f)

    post = await request.post()
    if post:
        isdigit_xy = lambda x, y: ''.join((x, y)).isdigit()
        new_id = lambda id: False if id in data else True
        empty_xy = lambda x, y: tuple(map(int, (x, y))) not in [(data[i]['x'], data[i]['y']) for i in data]
        less = lambda n: True if len(data) <= n else False

        d_type = post['type']
        if d_type == 'addItem':
            id, x, y = post['id'], post['x'], post['y']
            if isdigit_xy(x, y) and new_id(id) and empty_xy(x, y) and less(20):
                data[id] = {'x': int(x), 'y': int(y)}
        elif d_type == 'moveItem':
            id, x, y = post['id'], post['x'], post['y']
            if isdigit_xy(x, y) and not new_id(id) and empty_xy(x, y):
                data[id] = {'x': int(x), 'y': int(y)}
        elif d_type == 'removeItem':
            id = post['id']
            if (not new_id(id)) and (not less(10)):
                del data[id]

    with open('data.pickle', 'wb') as f: pickle.dump(data, f)
    
    return aiohttp_jinja2.render_template('index.html', request, {'data':data})


async def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route('GET', '/main', formshandler)
    app.router.add_route('POST', '/main', formshandler)
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(os.path.dirname(os.path.abspath(__file__))))
    srv = await loop.create_server(app.make_handler(),'127.0.0.1', 8080)
    print('Server started')
    return srv


loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
try: loop.run_forever()
except KeyboardInterrupt: pass