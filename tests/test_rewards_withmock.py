import unittest
from unittest.mock import patch
import os
import requests
import re

from open_r1.rewards import (
    request_auto,
    reward_remote_check_syntax,
    reward_remote_check_is_loop,
    reward_remote_is_loop_invariant_format,
    reward_remote_check_has_post_condition,
    reward_remote_check_is_cheating,
    reward_remote_verify,
    format_reward,
    tag_count_reward,
    reasoning_steps_reward,
    get_repetition_penalty_reward,
    get_code_format_reward,
)

# --- Helper classes and functions for mocking HTTP requests ---

class FakeResponse:
    def __init__(self, json_data, status_code=200):
        self._json = json_data
        self.status_code = status_code
    
    def json(self):
        return self._json
    
    def raise_for_status(self):
        if self.status_code != 200:
            raise requests.exceptions.HTTPError("Error", response=self)

def fake_post(url, json, timeout):
    # Extract the target endpoint from the URL (e.g. "check_syntax", "rewrite", etc.)
    target = url.split('/')[-1]
    if target == "check_syntax":
        # If the code contains an error ("Missing semicolon"), simulate lower score.
        if "Missing semicolon" in json["source_code"]:
            return FakeResponse({"check_syntax": "0.5"})
        else:
            return FakeResponse({"check_syntax": "1"})
    elif target == "check_is_loop":
        if "for(" in json["source_code"]:
            return FakeResponse({"check_is_loop": "1"})
        else:
            return FakeResponse({"check_is_loop": "0"})
    elif target == "is_loop_invariant_format":
        if "assert" in json["source_code"]:
            return FakeResponse({"is_loop_invariant_format": "1"})
        else:
            return FakeResponse({"is_loop_invariant_format": "0"})
    elif target == "check_has_post_condition":
        # For our test, we require both an assert and the literal "Post-condition:" comment.
        if "assert" in json["source_code"] and "Post-condition:" in json["source_code"]:
            return FakeResponse({"has_post_condition": "1"})
        else:
            return FakeResponse({"has_post_condition": "0"})
    elif target == "check_is_cheating":
        # If the code contains an assert with a hardcoded value (e.g. assert(5 == 5)),
        # we simulate a cheating flag.
        if "assert(5 == 5)" in json["source_code"].replace(" ", "") or "assert(5==5)" in json["source_code"].replace(" ", ""):
            return FakeResponse({"check_is_cheating": "1"})
        else:
            return FakeResponse({"check_is_cheating": "0"})
    elif target == "rewrite":
        # Simply echo back the source code as "new_code".
        return FakeResponse({"new_code": json["source_code"]})
    elif target == "lemur_verifier_with_prop":
        # For property "unreach-call", return status 1 (successful verification).
        if json.get("property", "unreach-call") == "unreach-call":
            return FakeResponse({"status": 1})
        else:
            return FakeResponse({"status": 0})
    else:
        return FakeResponse({}, 404)

# --- Sample completions used in tests ---

COMPLETIONS_SAMPLES = [
    [{"content": "```#include <stdio.h>\nint main() { printf(\"Hello, World!\\n\"); return 0; }```"}],
    [{"content": "```#include <stdio.h>\nint main() { for(int i = 0; i < 10; i++) printf(\"%d\\n\", i); return 0; }```"}],
    [{"content": "```#include <stdio.h>\nint main() { printf(\"Missing semicolon\") return 0; }```"}],
]

# --- Test Classes ---

class TestRemoteRewards(unittest.TestCase):

    @patch('open_r1.rewards.requests.post', side_effect=fake_post)
    def test_request_auto(self, mock_post):
        """Test request_auto with a successful mocked HTTP response."""
        payload = {"source_code": "value"}
        result = request_auto(payload, target_path="check_syntax")
        self.assertIsNotNone(result)
        self.assertIn("check_syntax", result)
        mock_post.assert_called_once()

    @patch('open_r1.rewards.requests.post', side_effect=fake_post)
    def test_remote_check_syntax(self, mock_post):
        """Test reward_remote_check_syntax with valid and invalid syntax."""
        completions = [
            [{"content": "```#include <stdio.h>\nint main() { printf(\"Hello, World!\\n\"); return 0; }```"}],
            [{"content": "```#include <stdio.h>\nint main() { printf(\"Missing semicolon\") return 0; }```"}]
        ]
        rewards = reward_remote_check_syntax(completions)
        self.assertEqual(len(rewards), 2)
        self.assertEqual(rewards[0], 1.0)  # Valid syntax gets reward 1.0
        self.assertLess(rewards[1], 1.0)   # Invalid syntax gets lower reward (0.5)

    @patch('open_r1.rewards.requests.post', side_effect=fake_post)
    def test_remote_check_is_loop(self, mock_post):
        """Test reward_remote_check_is_loop with loop and non-loop code."""
        completions = [
            COMPLETIONS_SAMPLES[1],  # Contains a loop: should return 1.0
            COMPLETIONS_SAMPLES[0]   # No loop: should return 0.0
        ]
        rewards = reward_remote_check_is_loop(completions)
        self.assertEqual(len(rewards), 2)
        self.assertEqual(rewards[0], 1.0)
        self.assertEqual(rewards[1], 0.0)

    @patch('open_r1.rewards.requests.post', side_effect=fake_post)
    def test_remote_is_loop_invariant_format(self, mock_post):
        """Test reward_remote_is_loop_invariant_format with proper invariant format."""
        completions = [
            [{"content": "```\n#include <stdio.h>\nint main() {\n    int sum = 0;\n    assert(sum == 0);\n    for (int i = 1; i <= 10; i++) {\n        assert(sum == 0);\n        sum += i;\n        assert(sum == 0);\n    }\n    return 0;\n}\n```"}],
        ]
        rewards = reward_remote_is_loop_invariant_format(completions)
        self.assertEqual(len(rewards), 1)
        self.assertEqual(rewards[0], 1.0)

    @patch('open_r1.rewards.requests.post', side_effect=fake_post)
    def test_remote_is_loop_invariant_format2(self, mock_post):
        """Test reward_remote_is_loop_invariant_format for code missing invariant asserts."""
        completions = [
            [{"content": "```\n#include <stdio.h>\nint main() {\n    int sum = 0;\n    assert(sum == 0);\n    for (int i = 1; i <= 10; i++) {\n        assert(sum == 0);\n        sum += i;\n        assert(sum == 0);\n    }\n    return 0;\n}\n```"}],
            [{"content": "```\n#include <stdio.h>\nint main() {\n    int sum = 0;\n    // Invariant: sum == i*(i+1)/2\n    for (int i = 1; i <= 10; i++) {\n        sum += i;\n    }\n    return 0;\n}\n```"}]
        ]
        rewards = reward_remote_is_loop_invariant_format(completions)
        self.assertEqual(len(rewards), 2)
        self.assertEqual(rewards[0], 1.0)  # Contains asserts → reward 1.0
        self.assertEqual(rewards[1], 0.0)  # Missing asserts → reward 0.0

    @patch('open_r1.rewards.requests.post', side_effect=fake_post)
    def test_remote_check_has_post_condition(self, mock_post):
        """Test reward_remote_check_has_post_condition with a valid post-condition."""
        completions = [[{"content": "```\n#include <assert.h>\nint main() {\n    int n = 10;\n    int sum = 0;\n    for (int i = 1; i <= n; i++) {\n        sum += i;\n    }\n    // Post-condition: sum == (n*(n+1))/2\n    assert(sum == (n*(n+1))/2);\n    return 0;\n}\n```"}]]
        rewards = reward_remote_check_has_post_condition(completions)
        self.assertEqual(len(rewards), 1)
        self.assertEqual(rewards[0], 1.0)

    @patch('open_r1.rewards.requests.post', side_effect=fake_post)
    def test_remote_check_is_cheating(self, mock_post):
        """Test reward_remote_check_is_cheating by detecting a cheating assert."""
        completions = [[{"content": "```\n#include <assert.h>\nint main() {\n    int a = 1, b = 2;\n    assert(a == 1);   // valid\n    assert(5 == 5);   // cheating: no context\n    return 0;\n}\n```"}]]
        rewards = reward_remote_check_is_cheating(completions)
        self.assertEqual(len(rewards), 1)
        self.assertEqual(rewards[0], 1.0)

    @patch('open_r1.rewards.requests.post', side_effect=fake_post)
    def test_remote_verify(self, mock_post):
        """Test reward_remote_verify with successful verification."""
        completions = [COMPLETIONS_SAMPLES[0]]
        rewards = reward_remote_verify(completions, property="unreach-call")
        self.assertEqual(len(rewards), 1)
        self.assertEqual(rewards[0], 1.0)

class TestFormattingRewards(unittest.TestCase):

    def test_format_reward(self):
        """Test format_reward for properly formatted and improperly formatted responses."""
        completions = [
            [{"content": "<think>\nReasoning\n</think>\n<answer>\nSolution\n</answer>"}],
            [{"content": "No proper tags here"}]
        ]
        rewards = format_reward(completions)
        self.assertEqual(rewards[0], 1.0)
        self.assertEqual(rewards[1], 0.0)

    def test_tag_count_reward(self):
        """Test tag_count_reward with both full and partial tags."""
        completions = [
            [{"content": "<think>\nReasoning\n</think>\n<answer>\nSolution\n</answer>"}],
            [{"content": "Reasoning\n</think>\n<answer>\nSolution\n</answer>"}]
        ]
        rewards = tag_count_reward(completions)
        self.assertEqual(rewards[0], 1.0)
        self.assertEqual(rewards[1], 0.75)

    def test_reasoning_steps_reward(self):
        """Test reasoning_steps_reward for various step counts."""
        completions = [
            [{"content": "Step 1: first\nStep 2: second\nStep 3: third"}],
            [{"content": "Step 1: only step"}]
        ]
        rewards = reasoning_steps_reward(completions)
        self.assertEqual(rewards[0], 1.0)
        self.assertAlmostEqual(rewards[1], 1/3)

    def test_repetition_penalty_reward(self):
        """Test repetition penalty reward with different repetition levels."""
        penalty_fn = get_repetition_penalty_reward(ngram_size=2, max_penalty=-1.0)
        completions = [
            [{"content": "this is a test"}],
            [{"content": "this this this this this"}]
        ]
        rewards = penalty_fn(completions)
        self.assertEqual(rewards[0], 0.0)
        self.assertAlmostEqual(rewards[1], -0.75)

    def test_code_format_reward(self):
        """Test get_code_format_reward with several formatting scenarios."""
        reward_fn = get_code_format_reward(language="python")
        completions = [
            [{"content": "<think>\nAnalysis\n</think>\n<answer>\n```python\ndef hello():\n    print('world')\n```\n</answer>"}],
            [{"content": "<think>\nAnalysis\n</think>\n<answer>\n```javascript\nconsole.log('hello');\n```\n</answer>"}],
            [{"content": "<think>\nAnalysis\n</think>\n<answer>\nJust plain text\n</answer>"}]
        ]
        rewards = reward_fn(completions)
        self.assertEqual(rewards[0], 1.0)
        self.assertEqual(rewards[1], 0.0)
        self.assertEqual(rewards[2], 0.0)

if __name__ == "__main__":
    unittest.main()
