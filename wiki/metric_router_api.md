# Metrics Router API
Metrics Router API is responsible for ingesting data from different IoT edge devices and routing it to the appropriate data storage. The API is designed to handle different types of data formats (e.g. numeric, text, binary, etc.) and provide a secure way to ingest data.

### Requirements
- Data Ingestion
- Data Processing
- Data Storage
- Security

### Data Format
- Numeric Data: integer, float, array (1D, 2D, 3D)
- Text Data: string
- Binary Data: JPEG, MP3, MP4 etc.

## gRPC Endpoints
```bash
# Endpoint to authenticate and get JWT token
rpc GetToken(AuthRequest) returns (AuthResponse)

# Numeric data ingestion (requires valid JWT token)
rpc SendNumericData(NumericDataRequest) returns (MetricsResponse)

# Binary data ingestion (requires valid JWT token)
rpc SendBinaryData(BinaryDataRequest) returns (MetricsResponse)

# Text data ingestion (requires valid JWT token)
rpc SendTextData(TextDataRequest) returns (MetricsResponse)

# Event data ingestion (requires valid JWT token)
rpc SendEventData(EventDataRequest) returns (MetricsResponse)
```

## References
- [Google](https://cloud.google.com/apis/design?hl=de)