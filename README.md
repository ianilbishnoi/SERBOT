# Autonomous Site Safety and Structural Site Inspection Robot

Mobile multi-sensor robot that monitors construction-site safety (PPE, gas, obstacles) and structural change (tilt, cracks).

## Team
| Member | Name | Reg. No. | Module |
|--------|------|----------|--------|
| 1 | Devargha Sinha | | |
| 2 | Sachin | | |
| 3 | Gavril Seth | | |
| 4 | Anil Bishnoi | | |

## Structure
| Folder | Contents |
|--------|----------|
| `literature/` | Paper summaries |
| `firmware_esp32/` | Sensor node (IMU, ultrasonic, DHT22, gas, buzzer) |
| `vision/` | PPE detection (YOLO), crack baseline, evaluation |
| `fusion/` | Filters, hazard score, change detection, metrics, tests |
| `dashboard/` | Flask web dashboard |
| `docs/` | Progress log |

## Data flow
ESP32 -> MQTT `site/sensors` -> `fusion/hazard_node.py` -> MQTT `site/alerts` -> dashboard + buzzer.

## Run
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest fusion/tests                                  # formulas and metrics
mosquitto -v                                         # MQTT broker (install Mosquitto)
cd fusion && python hazard_node.py --broker localhost
cd dashboard && python app.py --broker localhost      # open http://localhost:5000
python vision/detect_ppe.py --weights best.pt --source 0
```
Flash `firmware_esp32/sensor_node/sensor_node.ino` after setting Wi-Fi and the broker IP.

## Formulas and metrics
See `fusion/filters.py` and `fusion/metrics.py` (same as the Review 1 slides).

## Results (update after testing)
| Test | Metric | Value |
|------|--------|-------|
| PPE detection | Precision / Recall / mAP@0.5 | |
| Tilt vs inclinometer | MAE / RMSE (deg) | |
| Distance | % error | |
