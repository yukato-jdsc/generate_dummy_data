from __future__ import annotations

import csv
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "generate_csv.py"


class GenerateCsvCliTests(unittest.TestCase):
    maxDiff = None

    def run_script(
        self,
        output_dir: str,
        *args: str,
        expect_success: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        command = ["uv", "run", "python", str(SCRIPT), "--output-dir", output_dir, *args]
        completed = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if expect_success:
            self.assertEqual(
                completed.returncode,
                0,
                msg=f"stdout:\n{completed.stdout}\n\nstderr:\n{completed.stderr}",
            )
        return completed

    def read_csv(self, directory: Path, name: str) -> tuple[list[str], list[list[str]]]:
        with (directory / name).open("r", encoding="utf-8-sig", newline="") as fh:
            rows = list(csv.reader(fh))
        return rows[0], rows[1:]

    def generated_files(self, directory: Path) -> list[str]:
        return sorted(path.name for path in directory.glob("*.csv"))

    def test_default_run_generates_all_expected_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_dir = Path(tmp_dir)
            self.run_script(tmp_dir)

            files = self.generated_files(output_dir)
            self.assertEqual(
                files,
                [
                    "m_agency_all.csv",
                    "m_agency_diff.csv",
                    "m_campaign_all.csv",
                    "m_product_all.csv",
                ],
            )

            _, campaign_rows = self.read_csv(output_dir, "m_campaign_all.csv")
            _, agency_rows = self.read_csv(output_dir, "m_agency_all.csv")
            _, agency_diff_rows = self.read_csv(output_dir, "m_agency_diff.csv")
            _, product_rows = self.read_csv(output_dir, "m_product_all.csv")

            self.assertEqual(len(campaign_rows), 50)
            self.assertEqual(len(agency_rows), 1000)
            self.assertEqual(len(agency_diff_rows), 53)
            self.assertEqual(len(product_rows), 1000)

    def test_targets_campaign_only_generates_single_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_dir = Path(tmp_dir)
            self.run_script(tmp_dir, "--targets", "campaign")
            self.assertEqual(self.generated_files(output_dir), ["m_campaign_all.csv"])

    def test_same_seed_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as first_tmp, tempfile.TemporaryDirectory() as second_tmp:
            self.run_script(first_tmp, "--seed", "7")
            self.run_script(second_tmp, "--seed", "7")

            for name in [
                "m_campaign_all.csv",
                "m_agency_all.csv",
                "m_agency_diff.csv",
                "m_product_all.csv",
            ]:
                self.assertEqual(
                    (Path(first_tmp) / name).read_text(encoding="utf-8-sig"),
                    (Path(second_tmp) / name).read_text(encoding="utf-8-sig"),
                )

    def test_csv_headers_do_not_include_identity_id_column(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_dir = Path(tmp_dir)
            self.run_script(tmp_dir)

            for name in [
                "m_campaign_all.csv",
                "m_agency_all.csv",
                "m_agency_diff.csv",
                "m_product_all.csv",
            ]:
                header, _ = self.read_csv(output_dir, name)
                self.assertNotIn("id", header)

    def test_agency_diff_is_subset_of_agency_all(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_dir = Path(tmp_dir)
            self.run_script(tmp_dir, "--seed", "11")

            agency_header, agency_rows = self.read_csv(output_dir, "m_agency_all.csv")
            diff_header, diff_rows = self.read_csv(output_dir, "m_agency_diff.csv")
            self.assertEqual(agency_header, diff_header)

            index = agency_header.index("agent_code")
            agency_codes = {row[index] for row in agency_rows}
            diff_codes = [row[index] for row in diff_rows]
            self.assertEqual(len(diff_codes), 53)
            self.assertEqual(len(diff_codes), len(set(diff_codes)))
            self.assertTrue(set(diff_codes).issubset(agency_codes))


if __name__ == "__main__":
    unittest.main()
