# Device Management API
The Device Management API is responsible for managing IoT devices and their sensor types. The API provides endpoints to register, update, and remove devices, as well as to add and remove sensor types. The API also allows the creation of anomalies for sensor types.

### Requirements
- Register a new IoT device
- Retrieve a list of registered devices
- Retrieve device status
- Retrieve details for a specific device
- Update device information
- Remove a device from the system
- Adding new sensor type
- Remove sensor type
- Create anomalies for sensor type

**Authentication**
```
POST /token
Headers :
  Content - Type : application / json
Body : {
  "device_identifier": "device-identifier",
  "device_secret": "device-secret "
}
```

Once the JWT token is obtained, include it in the ‘Authorization‘ header of the requests.

Example:
```
Headers :
  Authorization : Bearer <jwt-token>
Content - Type : application / json
```


**Devices**
Getting status of specific devices
```
POST /api/v1/tenants/devices/states
Body : {tenant_identifier: ["000001"], "device_identifier": ["000001", "000002"]}
```

Register a new device
```
POST /api/v1/tenants/devices/register

Body : {
  "device_identifier": "000001",
  "tenant_identifier": "000001",
  "description": "",
  "timezone": "Europe/Zurich"
}
```

Updating a device
```
PUT /api/v1/tenants/devices/update

Body : {
  "device_identifier": "000001",
  "tenant_identifier": "000001",
  "description": "",
  "timezone": "Europe/London"
}
```

Remove a device
```
DELETE /api/v1/tenants/devices/remove

Body : {
  "device_identifier": "000001",
  "tenant_identifier": "000001"
}
```

**Sensor Types**

Adding new sensor type
```
POST /api/v1/tenants/devices/sensors/add

Body : {
  "device_identifier": "000001",
  "tenant_identifier": "000001",
  "sensor_type": "temperature",
  "unit": "°C",
  "min_value": -20,
  "max_value": 50
}
```

Get all sensor types from specific device
```
GET /api/v1/tenants/devices/sensors
```

Remove sensor
```
DELETE /api/v1/tenants/devices/sensors/sensor/remove

Body : {
  "device_identifier": "000001",
  "tenant_identifier": "000001",
  "sensor_identifier": "000001"
}
```

Get all sensor states from specific device
```
POST /api/v1/tenants/devices/sensors/states

Body : {"device_identifier": ["000001"], "tenant_identifier": ["000001"]}
```

Get a specific sensor state 
```
POST /api/v1/tenants/devices/sensors/sensor_identifier/states

Body : {"sensor_identifier": ["000001", "0002"], 
        "device_identifier": ["000001"],
        "tenant_identifier": ["000001"]}
```

Creating anomalies for sensor
```
POST /api/v1/tenants/devices/sensors/anomalies

Body : {
  "device_identifier": "000001",
  "sensor_identifier": "000001",
  "anomalies": [
    {
      "start": "2024-09-23T00:00:00Z",
      "end": "2024-09-23T00:00:00Z",
      "anomalie_type": "gaussian",
      "mean": 0,
      "std": 1
    }
  ]
}
```
