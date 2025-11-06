from enum import Enum


class WsMessageTypes(Enum):
  COMMAND = 'command'
  SENSOR_MANAGEMENT = 'sensor_management'
  CONNECT_ACK = 'connect_ack'


class WsSensorCommands(Enum):
  ''' Enum class for websocket sensor commands '''
  ADD_SENSOR = 'add_sensor'
  REMOVE_SENSOR = 'remove_sensor'
  GET_SENSORS = 'get_sensors'


class WsGeneralCommands(Enum):
  ''' Enum class for websocket general commands '''
  GET_CONNECTION_STATE = 'get_connection_state'


class FaultTypes(Enum):
  ''' Gear Vibration fault types '''
  ECCENTRICITY = 'eccentricity'
  MISSING_TOOTH = 'missing_tooth'
  NO_FAULT = 'no_fault'
  ROOT_CRACK = 'root_crack'
  SURFACE_FAULT = 'surface_fault'
  TOOTH_CHIPPED_FAULT = 'tooth_chipped_fault'
