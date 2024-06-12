from time import sleep
from pydbus import SystemBus
from gi.repository import GLib
from dbus.mainloop.glib import DBusGMainLoop

DBusGMainLoop(set_as_default=True)

# D-Bus 시스템 버스에 연결
bus = SystemBus()

# 블루투스 어댑터 가져오기
adapter = bus.get('org.bluez', '/org/bluez/hci0')

# 어댑터를 powered on 상태로 설정
adapter.Powered = True

# LEAdvertisingManager1 인터페이스 가져오기
adapter_path = "/org/bluez/hci0"
adapter_obj = bus.get("org.bluez", adapter_path)
le_advertising_manager = bus.get("org.bluez.LEAdvertisingManager1", adapter_path)

# 광고 데이터 설정
class Advertisement:
    def __init__(self, bus, index):
        self.path = f"/org/bluez/example/advertisement{index}"
        self.bus = bus
        self.ad_type = "peripheral"
        self.service_uuids = ["00001101-0000-1000-8000-00805F9B34FB"]
        self.local_name = "YongGulRiderService"
        self.include_tx_power = True

    def get_properties(self):
        return {
            "Type": self.ad_type,
            "ServiceUUIDs": self.service_uuids,
            "LocalName": self.local_name,
            "IncludeTxPower": self.include_tx_power,
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_to_connection(self):
        self.bus.publish(self.path, self)

advertisement = Advertisement(bus, 0)
advertisement.add_to_connection()

# 광고 등록
le_advertising_manager.RegisterAdvertisement(advertisement.get_path(), {})

print("Advertising...")

# 광고 유지
try:
    GLib.MainLoop().run()
except KeyboardInterrupt:
    print("Stopping advertising...")
    le_advertising_manager.UnregisterAdvertisement(advertisement.get_path())
    print("Advertising stopped.")
