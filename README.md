[![GitHub Release](https://img.shields.io/github/release/sopelj/hass-anycubic-printer-component.svg?style=for-the-badge)](https://github.com/sopelj/hass-anycubic-printer-component/releases)
[![License](https://img.shields.io/github/license/sopelj/hass-anycubic-printer-component.svg?style=for-the-badge)](LICENSE.md)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)
![Project Maintenance](https://img.shields.io/maintenance/yes/2022.svg?style=for-the-badge)

# Anycubic Integration for Home Assistant

## Installation

Custom integration to connect to the Anycubic 3D Printers that support their app.
Only just started working on this, but seem to be able to obtain some information.

## Installation

Add to HACS as custom repository:

<https://github.com/sopelj/hass-anycubic-printer-component>

And then add to your configuration.yaml and add sensors for your mug(s):

```yaml
anycubic:
  - ip_address: 192.168.2.123  # Replace with your Printer's IP Address
    port: 6000  # If your port is different from 6000
```
