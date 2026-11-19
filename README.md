# PB25 Home Assistant integration

Custom integration for the KMP PB25 pellet burner.

## Installation

Copy this integration directory to:

    custom_components/pb25

Restart Home Assistant, then add PB25 from Settings → Devices & services → Add integration. Enter the PB25 hostname or IP address. The default polling interval is 30 seconds and can be changed in the integration options.

Existing YAML configuration is imported into a config entry:

    pb25:
      host: 192.168.1.50
      scan_interval: 30

Once Home Assistant has imported the entry, remove the pb25 section from configuration.yaml.

## Data source

The integration requests the endpoint already used by the original implementation:

    http://<host>/data.html

It extracts a JSON object from the response and exposes the fields already present in the integration:

- ttop
- tRoom
- Flame
- mode
- alarm2
- alarm1
- glow
- amps

Numeric values are exposed as numbers even when the PB25 response encodes them as strings, for example "64" or "0.2". Text values such as STANDBY, OFF, and alarm messages remain text.

The integration does not assume that additional endpoints or fields exist.

## Notes

- Communication uses HTTP, matching the existing PB25 code.
- Keep the PB25 reachable only on a trusted local network.
- Numeric values must be finite numbers.
- Home Assistant must be able to reach the configured host.
