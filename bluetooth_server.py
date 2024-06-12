import asyncio
from bleak import BleakScanner, BleakAdvertiser

# 광고 데이터 설정
advertisement_data = {
    "local_name": "YongGulRiderService",
    "manufacturer_data": {
        0xFFFF: bytearray([0x01, 0x02, 0x03, 0x04])
    },
    "service_data": {
        "00001101-0000-1000-8000-00805F9B34FB": bytearray([0x05, 0x06, 0x07, 0x08])
    },
    "service_uuids": ["00001101-0000-1000-8000-00805F9B34FB"]
}

async def advertise():
    advertiser = BleakAdvertiser()
    await advertiser.start(advertisement_data)

    print("Advertising...")
    try:
        await asyncio.sleep(30)  # 광고를 30초 동안 유지
    finally:
        await advertiser.stop()
        print("Advertising stopped.")

asyncio.run(advertise())
