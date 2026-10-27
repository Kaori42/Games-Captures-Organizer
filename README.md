# Games-Captures-Organizer

Converts NVIDIA app HDR screenshots (`.jxr`) to SDR PNG using `hdrfix.exe`
(bundled, from [brion/hdrfix](https://github.com/brion/hdrfix)).

The NVIDIA app already stores captures in one folder per game:

    C:\Users\<you>\Videos\NVIDIA
        - Cyberpunk 2077
            - Cyberpunk 2077 Screenshot 2026.08.31 - 21.17.08.13.jxr
            - PNG                         <- created by this script
                - Cyberpunk 2077 Screenshot 2026.08.31 - 21.17.08.13.png
        - Forza Horizon 6
        - ...

## Usage

```powershell
pip install -r requirements.txt

# Convert everything under %USERPROFILE%\Videos\NVIDIA into <game>\PNG\
python main.py

# Other source folder, PNGs in a separate tree (<dst>\<game>\)
python main.py "D:\Captures\NVIDIA" --dst "D:\Captures\PNG"

# Only some games / skip some folders
python main.py -g "Cyberpunk 2077" -g "Forza Horizon 6"
python main.py -x Desktop -x Wingdk -x "Jdk-21.0.3.9-hotspot"

# See what would be converted
python main.py --dry-run

# Pass options to hdrfix after `--`
python main.py -- --tone-map hable --exposure 0.5
```

- Already converted captures are skipped, so the command can be re-run at any time
  (`--overwrite` to force). An interrupted run (Ctrl+C) never leaves a broken PNG.
- Conversions run in parallel (`-j`, default: half the CPU cores, at most 4).
- PNGs keep the capture date of the JXR.
- Exit code: `0` OK, `1` some conversions failed, `2` bad arguments, `130` interrupted.

## Tests

```powershell
python -m unittest -v
```
