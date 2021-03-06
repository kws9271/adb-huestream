"""Support for switches which integrates with other components."""
import logging, time
from ppadb.client import Client as AdbClient

import voluptuous as vol

from homeassistant.components.switch import PLATFORM_SCHEMA, SwitchDevice
from homeassistant.const import CONF_NAME, CONF_HOST, CONF_PORT
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

DOMAIN = "huestream"

CONF_ADB_HOST = "adb_host"
CONF_ADB_PORT = "adb_port"
DEFAULT_NAME = 'Huestream'
DEFAULT_ADB_HOST = '127.0.0.1'
DEFAULT_ADB_PORT = '5037'
DEFAULT_PORT = '5555'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
    vol.Optional(CONF_ADB_HOST, default=DEFAULT_ADB_HOST): cv.string,
    vol.Optional(CONF_ADB_PORT, default=DEFAULT_ADB_PORT): cv.port
})

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Template switch."""
    name = config.get(CONF_NAME)
    host = config[CONF_HOST]
    port = config.get(CONF_PORT)
    adb_host = config.get(CONF_ADB_HOST)
    adb_port = config.get(CONF_ADB_PORT)
    try:
        client = AdbClient(host=adb_host, port=adb_port)
        _LOGGER.info("adb server %s connected", adb_host)
        device = client.device(host+':'+str(port))
        _LOGGER.info("adb device %s connected", host+':'+str(port))
        if device == None:
            _LOGGER.error("There is no android device %s:%s", host, port)
            return None
    except:
        _LOGGER.error("There is no adb server %s:%s", adb_host, adb_port)
        return None
    add_entities([Huestream(name, host, device)])

class Huestream(SwitchDevice):
    """Representation of a Huestream switch."""
    def __init__(self, name, host, device):
        """Initialize the Huestream switch."""
        self._name = name
        self._host = host
        self._state = None
        self.device = device

    @property
    def unique_id(self):
        """Return the switch unique ID."""
        return self._host

    @property
    def name(self):
        """Return the name of the switch."""
        return self._name

    @property
    def is_on(self):
        """Return true if switch is on."""
        return (int(self.device.shell('am stack list | grep com.bullbash.huestream -c')) > 0)

    def turn_on(self, **kwargs):
        self.device.shell('am start com.bullbash.huestream/.EntertainmentMainActivity')
        time.sleep(3)
        self.device.shell('input keyevent KEYCODE_APP_SWITCH')
        self.device.shell('input keyevent ENTER')
        self.update

    def turn_off(self, **kwargs):
        self.device.shell('am force-stop com.bullbash.huestream')
        time.sleep(1)
        self.update

    def update(self):
        try:
            self._state = ( int(self.device.shell('am stack list | grep com.bullbash.huestream -c')) > 0 )
            _LOGGER.info("Huestream state updated to %s", self._state)
        except:
            _LOGGER.error("Reading status from %s", self._name)