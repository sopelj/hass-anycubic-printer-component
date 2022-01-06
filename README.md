[![GitHub Release](https://img.shields.io/github/release/sopelj/hass-anycubic-printer-component.svg?style=for-the-badge)](https://github.com/sopelj/hass-anycubic-printer-component/releases)
[![License](https://img.shields.io/github/license/sopelj/hass-anycubic-printer-component.svg?style=for-the-badge)](LICENSE.md)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)
![Project Maintenance](https://img.shields.io/maintenance/yes/2022.svg?style=for-the-badge)

# Anycubic Integration for Home Assistant

## Installation

Custom integration to connect to the Anycubic 3D Printers that support their app.
Only just started working on this, but seem to be able to obtain some information.

*Note*: I have only tested with the Photon Mono SE. Technically should work with other resin printers that support the app. I have no FDM printers from Anycubic to test with though, so I'm not sure what they return. 

## Installation

Add to HACS as custom repository:

<https://github.com/sopelj/hass-anycubic-printer-component>

And then add to your configuration.yaml and add sensors for your mug(s):

### Config Flow

- Go into Settings -> Devices 
- Choose "Add Integration"
- Search for "Anycubic"
- Enter the IP address and port (default is 6000) of your printer and hit next

### Yaml

*Note:* Not sure if I'll keep this option as they seem to be pushing the config flow which is much quicker, but for now it works for now.

```yaml
anycubic:
  - ip_address: 192.168.2.123  # Replace with your Printer's IP Address
    port: 6000  # If your port is different from 6000
```

## Usage

Quick example for usage in lovelace

![](./images/lovelace_example.png)

```yaml
- type: vertical-stack
  cards:
    - type: entity
      entity: sensor.anycubic_current_state
    - type: conditional
      conditions:
        - entity: sensor.anycubic_current_state
          state_not: Stopped
      card:
        type: gauge
        entity: sensor.anycubic_job_percentage
        min: 0
        max: 100
        name: Print Progress
    - type: conditional
      conditions:
        - entity: sensor.anycubic_current_state
          state: Printing
      card:
        type: entity
        entity: sensor.anycubic_estimated_finish_time
```