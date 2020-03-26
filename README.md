# homeassistant-metar
A sensor for METAR temperatures. https://en.wikipedia.org/wiki/METAR

## Configuration

To enable it, add the following lines to your `configuration.yaml`:

```yaml
# Example configuration.yaml entry
sensor:
  - platform: metar
    airport_name: Pisa
    airport_code: LIRP
    monitored_conditions:
      - time
      - temperature
      - wind
      - pressure
      - visibility
      - precipitation
      - sky
```

### Configuration Variables

-  airport_name

  (string)(Required) The airport name.

  -  airport_code

    (string)(Required) The *International Civil Aviation Organization*, *ICAO* code for the airport.

-  monitored_conditions

  (string)(Optional) What to read

It need metar python module.

It's a custom component so it must be downloaded under /custom_components folder.
