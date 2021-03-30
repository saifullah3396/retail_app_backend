import asyncio
import aio_pika


async def main(loop):
    connection = await aio_pika.connect_robust(
        "amqp://guest:guest@127.0.0.1/", loop=loop
    )
    print("connected")
    routing_key = "camera_events"

    channel = await connection.channel()    # type: aio_pika.Channel
    exchange = await channel.declare_exchange('topic')

    await exchange.publish(
        aio_pika.Message(
            body='Hello {}'.format(routing_key).encode()
        ),
        routing_key=routing_key
    )

    await connection.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()
