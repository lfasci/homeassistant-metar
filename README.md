# homeassistant-metar
A sensor for METAR temperatures. https://en.wikipedia.org/wiki/METAR

In configuration.yaml add the following lines

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
      
It neet metar for installation on dietpi or raspberry pi

cd /home/homeassistant/.pyenv/versions/3.6.3/envs/homeassistant-3.6.3
source bin/activate
python3 -m venv .
python3 -m pip install metar

It's a custom component so it must be downloaded under /custom_components folder.
