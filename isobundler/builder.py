"""Stage dropped files/folders and build a CD-ROM .iso with hdiutil."""

import shutil
import subprocess
import tempfile
from pathlib import Path


class IsoBuildError(Exception):
    """Raised when staging or building the ISO fails."""


def build_iso(input_paths, output_path, volume_name=None):
    """Build an ISO9660+Joliet .iso from the given files/folders.

    Dropping a single folder stages its *contents* at the ISO root (not the
    folder itself). Dropping loose files/multiple items stages them directly
    at the root.
    """
    input_paths = [Path(p) for p in input_paths]
    output_path = Path(output_path)
    if not input_paths:
        raise IsoBuildError("No files were given to bundle.")

    for path in input_paths:
        if not path.exists():
            raise IsoBuildError(f"'{path}' does not exist.")

    if volume_name is None:
        volume_name = _default_volume_name(input_paths, output_path)

    with tempfile.TemporaryDirectory(prefix="isobundler-") as staging:
        staging_dir = Path(staging)
        _stage(input_paths, staging_dir)

        if not any(staging_dir.iterdir()):
            raise IsoBuildError("Nothing to bundle -- the dropped item(s) are empty.")

        output_path.parent.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(
            [
                "hdiutil",
                "makehybrid",
                "-iso",
                "-joliet",
                "-ov",  # overwrite in place: keeps the same inode across
                        # rebuilds at the same path, which matters if the
                        # output is a live CD-ROM mount in a VM -- UTM (and
                        # likely other sandboxed hypervisors) grants file
                        # access via a security-scoped bookmark tied to a
                        # specific inode, and replacing the file (e.g. `rm`
                        # + recreate) silently invalidates that bookmark on
                        # the *next* VM boot with "Operation not permitted".
                        # Confirmed empirically (`ls -i` before/after) that
                        # `-ov` does not change the inode; without it,
                        # hdiutil instead refuses to run at all if the
                        # output file already exists.
                "-default-volume-name",
                volume_name,
                "-o",
                str(output_path),
                str(staging_dir),
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise IsoBuildError(
                f"hdiutil failed to build the ISO:\n{result.stderr.strip()}"
            )

    return output_path


def _stage(input_paths, staging_dir):
    if len(input_paths) == 1 and input_paths[0].is_dir():
        for item in input_paths[0].iterdir():
            _copy_into(item, staging_dir)
    else:
        for path in input_paths:
            _copy_into(path, staging_dir)


def _copy_into(path, staging_dir):
    destination = staging_dir / path.name
    if path.is_dir():
        shutil.copytree(path, destination)
    else:
        shutil.copy2(path, destination)


def _default_volume_name(input_paths, output_path):
    if len(input_paths) == 1:
        name = input_paths[0].stem if input_paths[0].is_file() else input_paths[0].name
    else:
        name = output_path.stem
    # hdiutil's default volume name only accepts a limited character set cleanly.
    name = "".join(c if c.isalnum() else "_" for c in name).strip("_")
    return name[:32] or "UNTITLED"
