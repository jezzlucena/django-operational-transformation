import asyncio
import json

from op_trans.redis_cli import RedisCli

async def send_messages(pubsub, done, send):
    while not done:
        message = pubsub.get_message()
        if message and type(message.get('data')) == bytes:
            await send({
                'type': 'websocket.send',
                'text': message.get('data').decode("utf-8")
            })
        else:
            await asyncio.sleep(0.5)


async def websocket_application(scope, receive, send):
    done = False

    while True:
        event = await receive()

        if event['type'] == 'websocket.connect':
            await send({ 'type': 'websocket.accept' })

        if event['type'] == 'websocket.disconnect':
            done = True
            break

        if event['type'] == 'websocket.receive':
            if event['text'] == 'ping':
                await send({
                    'type': 'websocket.send',
                    'text': 'pong!'
                })
            else:
                pubsub = RedisCli.get().pubsub()
                if event['text'].startswith('sub:cnv:'):
                    pubsub.psubscribe(event['text'])
                    await send_messages(pubsub, done, send)
                elif event['text'].startswith('unsub:cnv:'):
                    pubsub.punsubscribe(event['text'])
                    done = True
