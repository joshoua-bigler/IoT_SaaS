import os
# local
from edge_device.sensors.manager import SensorManager
from edge_device.device import Device
from edge_device.api.grpc_client import GrpcClient
from edge_device.sensors.manager import SimulationManager
from dotenv import load_dotenv

load_dotenv()
sensor_manager = SensorManager()
sensor_manager.load_sensors()
device = Device(device_identifier=os.getenv('DEVICE_IDENTIFIER'), tenant_identifier=os.getenv('TENANT_IDENTIFIER'))
grpc_client = GrpcClient(host=os.getenv('HUB_HOST_NAME'), port=int(os.getenv('HUB_PORT')))
sim_manager = SimulationManager(device=device, grpc_client=grpc_client, sensor_manager=sensor_manager)
