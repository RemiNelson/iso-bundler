import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from isobundler.builder import IsoBuildError, build_iso


def _hdiutil_available():
    return shutil.which("hdiutil") is not None


@unittest.skipUnless(_hdiutil_available(), "hdiutil is only available on macOS")
class BuildIsoTest(unittest.TestCase):
    def test_build_from_folder_stages_contents_at_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            source_dir = tmp / "design_files"
            source_dir.mkdir()
            (source_dir / "hello.txt").write_text("hello")
            sub = source_dir / "sub"
            sub.mkdir()
            (sub / "nested.txt").write_text("nested")

            output_path = tmp / "output.iso"
            result = build_iso([source_dir], output_path)

            self.assertEqual(result, output_path)
            self.assertTrue(output_path.exists())
            self._assert_iso_contains(output_path, ["hello.txt", "sub/nested.txt"])

    def test_build_from_loose_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            file_a = tmp / "a.txt"
            file_b = tmp / "b.txt"
            file_a.write_text("a")
            file_b.write_text("b")

            output_path = tmp / "loose.iso"
            build_iso([file_a, file_b], output_path)

            self._assert_iso_contains(output_path, ["a.txt", "b.txt"])

    def test_missing_input_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            with self.assertRaises(IsoBuildError):
                build_iso([tmp / "does_not_exist.txt"], tmp / "out.iso")

    def test_no_inputs_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(IsoBuildError):
                build_iso([], Path(tmp) / "out.iso")

    @staticmethod
    def _assert_iso_contains(iso_path, expected_relative_paths):
        with tempfile.TemporaryDirectory() as mount_point:
            attach = subprocess.run(
                ["hdiutil", "attach", "-nobrowse", "-mountpoint", mount_point, str(iso_path)],
                capture_output=True,
                text=True,
            )
            assert attach.returncode == 0, attach.stderr
            try:
                for relative in expected_relative_paths:
                    assert (Path(mount_point) / relative).exists(), relative
            finally:
                subprocess.run(
                    ["hdiutil", "detach", mount_point, "-quiet"],
                    capture_output=True,
                    text=True,
                )


if __name__ == "__main__":
    unittest.main()
