# LAN Guardian — Public Demo

LAN Guardian is an educational cybersecurity project that demonstrates
how local network monitoring tools can identify changes in observed devices.

## Features

- View fictional network-device information.
- Explore simulated scan history.
- Review example security events.
- View a sample security report.
- Learn about the limitations of network monitoring.

## How the Demo Works

This public demonstration uses fictional devices and simulated scan results.
It does not inspect your actual network or use your private LAN Guardian data.

## Technology

- Python
- Streamlit

## Run Locally

Install the required dependency:

```powershell
python -m pip install -r requirements.txt
```

Start the public demo:

```powershell
python -m streamlit run public_demo.py
```

Open the local URL displayed in the terminal.

## Limitations

- All devices and scan results are fictional.
- The demo does not scan real networks.
- An unfamiliar device is not automatically malicious.
- This educational demonstration is not a production intrusion-detection system.

## Disclaimer

This project is intended for educational demonstration only.
Do not interpret simulated results as evidence of real network activity.
