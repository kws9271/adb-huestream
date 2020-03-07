"""Support for switches which integrates with other components."""
import logging, time
from ppadb.client import Client as AdbClient

import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from homeassistant.components.switch import (
    DOMAIN,
    ENTITY_ID_FORMAT,
    PLATFORM_SCHEMA,
    SwitchDevice,
)
from homeassistant.const import (
    CONF_HOST,
    CONF_PORT,
    CONF_ADB_HOST,
    CONF_ADB_PORT,
    CONF_NAME
)

DEFAULT_ADB_HOST = '127.0.0.1'
DEFAULT_ADB_PORT = '5037'
DEFAULT_PORT = '5555'
DEFAULT_NAME = 'Huestream'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
	vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
	vol.Optional(CONF_ADB_HOST, default=DEFAULT_ADB_HOST): cv.string,
    vol.Optional(CONF_ADB_PORT, default=DEFAULT_ADB_PORT): cv.port,
	vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string
})

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Template switch."""
	host = config.get(CONF_HOST)
	port = config.get(CONF_PORT)
	adb_host = config.get(CONF_ADB_HOST)
	adb_port = config.get(CONF_ADB_PORT)
	name = config.get(CONF_NAME)
    add_entities([Huestream(host, port, adb_host, adb_port, name)])

class Huestream(SwitchDevice):
    """Representation of a Huestream switch."""
    def __init__(self, host, port, adb_host, adb_port, name):
        """Initialize the Huestream switch."""
        self._state = None
        self._host = host
        self._port = port
        self._adb_host = adb_host
        self._adb_port = adb_port
        self._name = name
        self.device = None
        try:
            client = AdbClient(host=self._adb_host, port=self._adb_port)
            try:
                self.device = client.device(self._adb_host+self._adb_port)
            except:
                _Logger.error("There is no android device %s:%s", self._adb_host, self._adb_port)
                return None
        except:
            _Logger.error("There is no adb server %s:%s", self._host, self._port)
            return None

    @property
    def name(self):
        """Return the name of the switch."""
        return self._name

    def turn_on(self, **kwargs):
        self.device.shell('am start com.bullbash.huestream/.EntertainmentMainActivity')
        time.sleep(2)
        self.device.shell('input keyevent KEYCODE_APP_SWITCH')
        self.device.shell('input keyevent ENTER')

    def turn_off(self, **kwargs):
        self.device.shell('am force-stop com.bullbash.huestream')

    def update(self):
        if self.device.shell('am force-stop com.bullbash.huestream') == 1:
            self._state = True
        else:
            self._state = False




# from homeassistant.core import callback
# from homeassistant.exceptions import TemplateError
# from homeassistant.helpers.entity import generate_entity_id
# from homeassistant.helpers.event import track_state_change
# from homeassistant.helpers.script import Script

# from . import extract_entities, initialise_templates
# from .const import CONF_AVAILABILITY_TEMPLATE

# _LOGGER = logging.getLogger(__name__)
# _VALID_STATES = [STATE_ON, STATE_OFF, "true", "false"]

# ON_ACTION = "turn_on"
# OFF_ACTION = "turn_off"

# SWITCH_SCHEMA = vol.Schema(
#     {
#         vol.Required(CONF_VALUE_TEMPLATE): cv.template,
#         vol.Optional(CONF_ICON_TEMPLATE): cv.template,
#         vol.Optional(CONF_ENTITY_PICTURE_TEMPLATE): cv.template,
#         vol.Optional(CONF_AVAILABILITY_TEMPLATE): cv.template,
#         vol.Required(ON_ACTION): cv.SCRIPT_SCHEMA,
#         vol.Required(OFF_ACTION): cv.SCRIPT_SCHEMA,
#         vol.Optional(ATTR_FRIENDLY_NAME): cv.string,
#         vol.Optional(ATTR_ENTITY_ID): cv.entity_ids,
#     }
# )

# PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
#     {vol.Required(CONF_SWITCHES): cv.schema_with_slug_keys(SWITCH_SCHEMA)}
# )