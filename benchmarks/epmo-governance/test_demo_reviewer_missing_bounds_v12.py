"""Guard short fictional demonstration against private or exaggerated claims."""
import contextlib
import io
import unittest
from demo_reviewer_missing_bounds_45s import main


class DemonstrationContract(unittest.TestCase):
    def test_demonstration_has_expected_fictional_boundaries(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            main()
        text = output.getvalue()
        self.assertIn("0 human reviewers | 0 external actions", text)
        self.assertIn("NOT confidence intervals", text)
        self.assertIn("null_selective_treatment_dropout", text)
        self.assertIn("zero included=True", text)

    def test_demo_deterministic(self):
        a, b = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(a):
            main()
        with contextlib.redirect_stdout(b):
            main()
        self.assertEqual(a.getvalue(), b.getvalue())


if __name__ == "__main__":
    unittest.main()
