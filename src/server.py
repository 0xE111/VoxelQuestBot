from fastapi import FastAPI, Header, Response, HTTPException
from environs import Env

env = Env()
app = FastAPI()


SERVER_API_KEY = env('SERVER_API_KEY')


@app.get('/')
async def root():
    return Response(
        content=f'Мы переезжаем на v2. Все изменения в /docs. Используйте временный ключ для доступа к api: {SERVER_API_KEY}',
        media_type='text/html',
        status_code=302,
        headers={
            'Location': '/',
        },
    )


@app.get('/api/v2/location')
async def location(
    api_key: str | None = Header(default=None),
):
    if api_key != SERVER_API_KEY:
        raise HTTPException(status_code=403, detail={'error': 'wrong key'})

    results = [
        {
            'device_id': device_id,
            'location': None,
            'status': 'destroyed',
        } for device_id in range(64)
    ]

    results[18].update({
        'location': ['68.946192', '94.506208'],
        'status': 'operational',
    })

    results[33].update({
        'location': ['9223372036854775807', '9223372036854775807'],
        'status': 'corrupted',
    })

    results[10].update({
        'location': ['68.388253', '175.169301'],
    })

    results[34].update({
        'location': ['59.817252', '153.020863'],
    })

    results[60].update({
        'location': ['62.356226', '113.887236'],
    })

    return results
