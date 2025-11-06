## GraphQL

- [Strawberry](https://strawberry.rocks/)


## GraphQL with [Strawberry](https://strawberry.rocks/docs/integrations/fastapi)

**GraphQL Request**

```json
query MyQuery {
  numericScalarModel(
    body: {
            tenantIdentifier: "100000", 
            deviceIdentifier: "000001", 
            start: "2025-07-09", 
            end: "2025-07-10", 
      			metricIdentifier: ["vibration.gear1.x_axis", "vibration.gear1.y_axis"],
            model: {name: "gear_vibration_cnn_w_256", modelType: PYTORCH, windowSize: 256, version: "1"}, 
            path: ""}
  )
   {
    deviceIdentifier
    metricIdentifier
    unit
    model {
      name
      predicted
      probability
    }
    values {
      timestampLocal
      value
    }
  }
}
```

```json
query MyQuery {
  numericScalar(
    body: {
           tenantIdentifier: "100000", 
           deviceIdentifier: "000001", 
           start: "2025-04-14", 
           end: "2025-04-23", 
           path: "conveyor.motor1"}
  ) {
    deviceIdentifier
    metricIdentifier
    unit
    values {
      timestampLocal
      value
    }
  }
}
```

```json
query MyQuery {
  devices(body: {tenantIdentifier: "100000"}) {
    country
    description
    deviceIdentifier
    lat
    latestAliveLocal
    long
    status
    timezone
  }
}
```

```json


**Response**

```json
{
  "data": {
    "numericMetrics": [
      {
        "deviceIdentifier": "100000",
        "metricIdentifier": "sheet_counter_stacker",
        "unit": "sheets",
        "aggregation": "SUM",
        "analysis": "FAULT_DETECTION",
        "values": [
          {
            "value": 94,
            "timestampLocal": "2024-01-01T00:00:00",
            "date": "Monday, 2024-01-01"
          },
          {
            "value": 31,
            "timestampLocal": "2024-01-02T00:00:00",
            "date": "Tuesday, 2024-01-02"
            
          }
        ],
        "model": {
          "name": "CNN",
          "predicted": "eccentricity",
          "probability": 0.95
        }
      }
    ]
  }
}
```
