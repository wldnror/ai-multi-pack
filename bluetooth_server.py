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

# 광고 설정
advertisement = {
    'Type': 'peripheral',
    'LocalName': 'YongGulRiderService',
    'ServiceUUIDs': ['00001101-0000-1000-8000-00805F9B34FB']
}

# 광고 등록
ad_manager = bus.get('org.bluez', '/org/bluez')
path = '/org/bluez/example/advertisement0'
ad_manager.RegisterAdvertisement(path, advertisement, {})

print("Advertising...")

# 광고 유지
try:
    GLib.MainLoop().run()
except KeyboardInterrupt:
    print("Stopping advertising...")
    ad_manager.UnregisterAdvertisement(path)
    print("Advertising stopped.")
