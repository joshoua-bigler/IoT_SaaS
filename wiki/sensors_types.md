# Sensor Types
## Type of Component
- Robot Arm
- Pendulum
- Motor
- Camera
  - Detection of human movement
- Temperature
- Humidity
- Air Quality
- Pressure
- Optical Sensors
  - Luminance
- Ultrasonic Sensoren
  - Detect the distance of objects
- Accelerometers 
  - Measure acceleration forces to detect movement or tilt.
- Vibration Sensors  
- Audio
- Flow Meters
- GPS Sensors
- RFID Sensors
  - Simulate proximity and object identification.
- Solar Energy Monitors: Monitor solar panel performance.
- Wind speed
  - Predict energy based on wind speed
- Solar Energy 
  - Predict energy based on uv rays
- Event Logs

## Type of Data
### Numerical Data
**Scalar Values**
- Temperature: 25 °C
- Humidity: 50%

**Vectors (1D Arrays)**
- GPS coordinates: [Latitude, Longitude]

**Multidimensional Arrays**
- Greyscale image: 2D array e.g. [28, 28] 
- RGB-image: 3D array [28, 28, 3] 

### Text Data
- Object detection e.g. 'car', 'person'
- Jobs statistics e.g. 'job xy with consumables xy'
- RFID Tag ID's: 'ID12345ABC'  

### Binary Data
- Images: JPEG, PNG, BMP, TIFF
- Audio: MP3, WAV, FLAC
- Video: MP4, AVI, MKV

## Data Format
**Numerical Data**
- Integer
- Float
- Array (1D, 2D, 3D, ..., nD)

**Text Data**
- String

**Binary Data Formats**
- Images: JPEG, PNG, BMP, TIFF
- Audio: MP3, WAV, FLAC
- Video: MP4, AVI, MKV 

## Evaluate Data Volume
- Number of devices
- Number of sensors per device 
- Sample rate: sample/second 
- Data size per sample

**Data Volume**<br>
Data Volume = Number of Devices×Number of Sensors per Device×Samples per Time×Data Size per Sample

**Storage**<br>
Retention time: based on the data retention time the data storage will increase over time more


**Network Traffic**<br>
Total Data Transmission Volume = Total Data Volume×Frequency of Data Transmission


![total_data_volume](/images/data_volumes/total_data_volume.png)

**Estimated Data Volume and Network Traffic**
- Devices: 100
- Sensors per device: 100
- Sample rate: 1 sample/min
- Data size per sample: 16 bytes
- Data retention: 36 months

<u>Data Volume</u> = <u>235.0 GB</u><br>
<u>Network Traffic</u> = <u>20.8 kbps</u>

![Data Volume for 100 Devices, 100 Sensors, 1 Sample/Min, 16 Bytes](/images/data_volumes/data_volume_d100_s100_sm1_ds16.png)

## Selected Sensor Types
Focus on industrial sensors

- Temperature values
- Humidity values
- Robot arm

## Sensor Simulation
### Temperature Sensor
1. Option 1: Simulate temperature values based on a given dataset
2. Option 2: Simulate temperature values based on a physics-based model
3. Option 3: Simulate temperature values based on a random walk model


**References**
[Kaggle: Room Temperature](https://www.kaggle.com/datasets/vitthalmadane/ts-temp-1)
[PyBullet](https://github.com/bulletphysics/bullet3)




**Data Source Options**
- [UCI Dataset](https://archive.ics.uci.edu/datasets)
- [Kaggle](https://www.kaggle.com/)
- [Frauenhofer](https://www.bigdata-ai.fraunhofer.de/s/datasets/index.html)
- [Meteomatics API](https://www.meteomatics.com/en/api/getting-started/)]
- Simulate Data -> physics based machine learning?
- Steinemann DPE -> belt position -> outlier detection 
- Steinemann Technology -> temperature curve bearings based on the load

## Appendix

