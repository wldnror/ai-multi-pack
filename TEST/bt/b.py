import asyncio
from bleak import BleakClient

async def run(address):
    async with BleakClient(address) as client:
        model_number = await client.read_gatt_char("00002a24-0000-1000-8000-00805f9b34fb")
        print("Model Number: {0}".format("".join(map(chr, model_number))))

address = "D8:3A:DD:3F:F8:84"  # 라즈베리파이의 MAC 주소
loop = asyncio.get_event_loop()
loop.run_until_complete(run(address))
