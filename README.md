# iso-bundler

A small drag-and-drop app that bundles files/folders into a CD-ROM `.iso`
image, for loading into the Windows 98 VM (QEMU/UTM) used for the Janome
Customizer 2000 in this restoration project. Attaching a `.iso` as a virtual
CD-ROM is a simple, reliable way to get files into an old VM that doesn't
have easy shared-folder support.

## Requirements

- **macOS only.** It shells out to `hdiutil`, the disk-image tool built into
  macOS — there's no Windows/Linux equivalent bundled here.
- Python 3.9+

## Installation

```sh
git clone https://github.com/RemiNelson/iso-bundler.git
cd iso-bundler
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

Build a double-clickable app (once, after installation above):

```sh
packaging/make_app.sh
```

This creates `~/Applications/ISO Bundler.app`, a thin wrapper around this
project's venv — launch it from Finder or Spotlight like any other app. If it
fails to open, check `~/Library/Logs/isobundler.log`. Re-run the script any
time after updating dependencies or moving the project folder, since the
wrapper hardcodes an absolute path to this repo's venv.

The app icon (`packaging/icon.icns`) is pre-generated and committed, so you
don't need anything extra to build the app. To regenerate it (e.g. after
tweaking `packaging/make_icon.py`), install Pillow and re-run it, then
rebuild the app:

```sh
.venv/bin/pip install pillow
.venv/bin/python packaging/make_icon.py
packaging/make_app.sh
```

Pillow is only needed for that regeneration step, so it's deliberately left
out of `requirements.txt`. If macOS keeps showing the old icon after
rebuilding, it's an icon-cache issue, not a build issue -- `killall Finder`
usually clears it.

Alternatively, run it directly from a terminal:

```sh
python -m isobundler
```

Either way, a window opens with a drop zone. Either:

- **Drag and drop** files and/or a folder onto it, or
- **Click it** to open a file picker.

Do this as many times as you like — each pass adds to a queue shown in the
list below the drop zone (duplicates are skipped). When you're done, click
**Build ISO...** to choose where to save the `.iso` and bundle everything
queued up. **Clear** empties the queue without building anything.

A few notes on what gets bundled:

- Drop a **single folder** and its *contents* become the root of the ISO
  (not the folder itself wrapping them).
- Drop **loose files** (or multiple items) and they're placed directly at
  the root of the ISO.

The resulting image is a hybrid ISO9660 + Joliet disc, so long filenames
survive — plain ISO9660 alone is limited to 8.3 filenames, which Joliet
(supported since Windows 95) fixes.

## Loading it into the VM

In UTM (or QEMU directly), attach the `.iso` as a CD-ROM drive to the
Windows 98 VM, boot/reboot it, and it'll show up as a CD in "My Computer" —
same as any other CD-ROM.

## Running the tests

```sh
python -m unittest discover -s tests -v
```

## License

This project is licensed under the **GNU General Public License v3.0**,
with the **Commons Clause** added on top:

- Free to use, modify, and share, including for personal/hobbyist use.
- **Not** licensed for commercial use (selling, paid hosting, bundling
  into a paid product) without a separate commercial license from the
  copyright holder.

See the [LICENSE](LICENSE) file for the full text.
