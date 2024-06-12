from pydbus import SystemBus
from gi.repository import GLib

class Advertisement:
    PATH = "/org/bluez/example/advertisement"

    def __init__(self, bus):
        self.bus = bus
        self.ad_path = self.PATH
        self.service_uuids = ['12345678-1234-5678-1234-56789abcdef0']

    def get_properties(self):
        return {
            'Type': 'peripheral',
            'ServiceUUIDs': self.service_uuids,
            'LocalName': 'YongGulRiderService',
            'Includes': ['tx-power'],
        }

    def get_path(self):
        return self.ad_path

    def Release(self):
        pass

def register_advertisement(bus):
    adapter = bus.get("org.bluez", "/org/bluez/hci0")
    adapter_props = bus.get("org.freedesktop.DBus.Properties", "/org/bluez/hci0")
    adapter_props.Set("org.bluez.Adapter1", "Powered", GLib.Variant("b", True))

    ad_manager = bus.get("org.bluez.LEAdvertisingManager1", "/org/bluez/hci0")
    advertisement = Advertisement(bus)
    ad_manager.RegisterAdvertisement(advertisement, {}, reply_handler=register_ad_cb, error_handler=register_ad_error_cb)
    GLib.MainLoop().run()

def register_ad_cb():
    print("Advertisement registered successfully")

def register_ad_error_cb(error):
    print("Failed to register advertisement:", error)
    GLib.MainLoop().quit()

bus = SystemBus()
register_advertisement(bus)
