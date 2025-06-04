# Discord Audio Pipe

[![GitHub Workflow Status](https://github.com/QiCuiHub/discord-audio-pipe/workflows/CI/badge.svg)](https://github.com/QiCuiHub/discord-audio-pipe/actions?query=workflow%3ACI)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/QiCuiHub/discord-audio-pipe)](https://github.com/QiCuiHub/discord-audio-pipe/releases/latest)

A simple and powerful program to pipe stereo audio (microphone, stereo mix, virtual audio cable, etc.) into a Discord bot. Perfect for streaming audio from your system to Discord voice channels.

## Features

- 🎤 Stream any audio source to Discord
- 🖥️ Simple GUI interface
- ⌨️ Command-line interface for automation
- 🔍 Device and channel querying tools
- 📝 Detailed logging for troubleshooting
- 🔄 Multiple simultaneous connections

## Quick Start

### Download

You can download the latest release [**here**](https://github.com/QiCuiHub/discord-audio-pipe/releases)

### Bot Setup

1. Create a Discord bot following [Discord's guide](https://discord.com/developers/docs/getting-started)
2. Enable the following bot permissions:
   - `View Channels`
   - `Connect`
   - `Speak`
3. Create a `token.txt` file in the program directory and paste your bot token

### Running the Program

- **Windows**: Double-click the `.exe` file
- **Source Code**: Run `python main.pyw`
- **CLI Mode**: See [Command Line Usage](#command-line-usage)

## Installation

### Windows

1. Download the latest `.exe` release
2. No additional installation required

### macOS

```bash
# Install dependencies
brew install portaudio --HEAD
brew install opus

# Install Python dependencies
pip install -r requirements.txt
```

### Linux

```bash
# Install system dependencies
sudo apt-get install libportaudio2 libxcb-xinerama0 libopus0

# Install Python dependencies
pip install -r requirements.txt
```

## Command Line Usage

```text
usage: main.pyw [-h] [-t TOKEN] [-v] [-c CHANNEL] [-d DEVICE] [-D] [-C]

Discord Audio Pipe

optional arguments:
  -h, --help            show this help message and exit
  -t TOKEN, --token TOKEN
                        The token for the bot
  -v, --verbose         Enable verbose logging

Command Line Mode:
  -c CHANNEL, --channel CHANNEL
                        The channel to connect to as an id
  -d DEVICE, --device DEVICE
                        The device to listen from as an index

Queries:
  -D, --devices         Query compatible audio devices
  -C, --channels        Query servers and channels (requires token)
```

## Troubleshooting

### Common Issues

#### Opus Library Not Found

- **macOS**: Ensure Opus is installed via Homebrew: `brew install opus`
- **Linux**: Install Opus: `sudo apt-get install libopus0`

#### No Audio Devices Found

- Check if your audio device is properly connected
- Ensure the device is not being used by another application
- Try running with `-D` flag to list available devices

#### Bot Can't Join Voice Channel

- Verify bot permissions in Discord server settings
- Check if the bot has been invited with proper permissions
- Ensure the bot is not already in another voice channel

### Logs

Logs are stored in the `logs` directory:

- `DAP_errors.log`: Contains error messages and stack traces
- `discord.log`: Contains debug information (when verbose mode is enabled)

## Development

### Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`

### Building

```bash
# Install build dependencies
pip install pyinstaller

# Build executable
python -m PyInstaller build/main.spec
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
