import unittest
from privacy_protocol_core.interpretation.interpreter import Interpreter

class TestInterpreter(unittest.TestCase):

    def setUp(self):
        self.interpreter = Interpreter()

    def test_translate_clause_basic(self):
        clause = "We may collect your personal data."
        expected_translation_prefix = "Plain language for:"
        translation = self.interpreter.translate_clause(clause)
        self.assertTrue(translation.startswith(expected_translation_prefix))
        self.assertIn(clause, translation)

    def test_identify_potential_issues_empty(self):
        policy_text = "This policy is perfectly clear and raises no issues."
        issues = self.interpreter.identify_potential_issues(policy_text)
        self.assertEqual(issues, [])

    # TODO: Add more tests as interpreter logic is implemented
    # def test_identify_potential_issues_with_known_problem(self):
    #     policy_text = "We sell your data to everyone." # A clearly problematic statement
    #     issues = self.interpreter.identify_potential_issues(policy_text)
    #     self.assertTrue(len(issues) > 0)

if __name__ == '__main__':
    unittest.main()
