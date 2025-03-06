
import unittest
import os
import requests
# from reward_functions.remote_rewards import (
from open_r1.rewards import (
    request_auto,
    reward_remote_check_syntax as remote_check_syntax,
    reward_remote_check_is_loop as remote_check_is_loop,
    reward_remote_is_loop_invariant_format as remote_is_loop_invariant_format,
    reward_remote_check_has_post_condition as remote_check_has_post_condition,
    reward_remote_check_is_cheating as remote_check_is_cheating,
    reward_remote_verify as remote_verify,
    format_reward,
    tag_count_reward,
    reasoning_steps_reward,
    get_repetition_penalty_reward,
    get_code_format_reward,
)

# Sample completions for testing
COMPLETIONS_SAMPLES = [
    [{"content": "```#include <stdio.h>\nint main() { printf(\"Hello, World!\\n\"); return 0; }```"}],
    [{"content": "```#include <stdio.h>\nint main() { for(int i = 0; i < 10; i++) printf(\"%d\\n\", i); return 0; }```"}],
    [{"content": "```#include <stdio.h>\nint main() { printf(\"Missing semicolon\") return 0; }```"}],
]

class TestRemoteRewards(unittest.TestCase):
    def test_request_auto(self):
        """Test request_auto with a successful response."""
        payload = {"key": "value"}
        result = request_auto(payload, target_path="")
        self.assertIsNone(result)

    def test_remote_check_syntax(self):
        """Test remote_check_syntax with valid and invalid syntax."""
        completions = [
            [{"content": """```#include <stdio.h>\nint main() { printf("Hello, World!\\n"); return 0; }```"""}],
            [{"content": """```#include <stdio.h>\nint main() { printf("Missing semicolon") return 0; }```"""}]
        ]
        rewards = remote_check_syntax(completions)
        self.assertEqual(len(rewards), 2)
        self.assertEqual(rewards[0], 1.0)  # Valid syntax
        self.assertLess(rewards[1], 1.0)   # Invalid syntax

    def test_remote_check_is_loop(self):
        """Test remote_check_is_loop with loop and non-loop code."""
        completions = [
            COMPLETIONS_SAMPLES[1],  # Code with loop
            COMPLETIONS_SAMPLES[0]   # Code without loop
        ]
        rewards = remote_check_is_loop(completions)
        self.assertEqual(len(rewards), 2)
        self.assertEqual(rewards[0], 1.0)  # Has loop
        self.assertEqual(rewards[1], 0.0)  # No loop

    def test_remote_is_loop_invariant_format(self):
        """Test remote_is_loop_invariant_format with proper and improper invariants."""
        completions = [
            [{"content": """```
#include <stdio.h>
int main() {
    int sum = 0;
    assert(sum == 0);
    for (int i = 1; i <= 10; i++) {
    assert(sum == 0);
        sum += i;
    assert(sum == 0);
    }
    return 0;
}
            ```"""}],
        ]
        rewards = remote_is_loop_invariant_format(completions)
        self.assertEqual(len(rewards), 1)
        self.assertEqual(rewards[0], 1.0)  # Proper invariant with asserts


    def test_remote_is_loop_invariant_format2(self):
        """Test remote_is_loop_invariant_format with proper and improper invariants."""
        completions = [
            [{"content": """```
#include <stdio.h>
int main() {
    int sum = 0;
    assert(sum == 0);
    for (int i = 1; i <= 10; i++) {
    assert(sum == 0);
        sum += i;
    assert(sum == 0);
    }
    return 0;
}
            ```"""}],
            [{"content": """```
#include <stdio.h>
int main() {
    int sum = 0;
    // Invariant: sum == i*(i+1)/2
    for (int i = 1; i <= 10; i++) {
        sum += i;
    }
    return 0;
}
            ```"""}]
        ]
        rewards = remote_is_loop_invariant_format(completions)
        self.assertEqual(len(rewards), 2)
        self.assertEqual(rewards[0], 1.0)  # Proper invariant with asserts
        self.assertEqual(rewards[1], 0.0)  # Missing asserts

    def test_remote_check_has_post_condition(self):
        """Test remote_check_has_post_condition with valid post-condition."""
        completions = [[{"content": """```
#include <assert.h>
int main() {
    int n = 10;
    int sum = 0;
    for (int i = 1; i <= n; i++) {
        sum += i;
    }
    // Post-condition: sum == (n*(n+1))/2
    assert(sum == (n*(n+1))/2);
    return 0;
}
        ```"""}]]
        rewards = remote_check_has_post_condition(completions)
        self.assertEqual(len(rewards), 1)
        self.assertEqual(rewards[0], 1.0)

    def test_remote_check_is_cheating(self):
        """Test remote_check_is_cheating with cheating assert."""
        completions = [[{"content": """```
#include <assert.h>
int main() {
    int a = 1, b = 2;
    assert(a == 1);   // valid
    assert(5 == 5);   // cheating: no context
    return 0;
}
        ```"""}]]
        rewards = remote_check_is_cheating(completions)
        self.assertEqual(len(rewards), 1)
        self.assertEqual(rewards[0], 1.0)  # Indicates cheating detected

    def test_remote_verify(self):
        """Test remote_verify with successful verification."""
        completions = [COMPLETIONS_SAMPLES[0]]
        rewards = remote_verify(completions, property="unreach-call")
        self.assertEqual(len(rewards), 1)
        self.assertEqual(rewards[0], 1.0)

class TestFormattingRewards(unittest.TestCase):
    def test_format_reward(self):
        """Test format_reward with correct and incorrect formats."""
        completions = [
            [{"content": "<think>\nReasoning\n</think>\n<answer>\nSolution\n</answer>"}],
            [{"content": "No proper tags here"}]
        ]
        rewards = format_reward(completions)
        self.assertEqual(rewards[0], 1.0)
        self.assertEqual(rewards[1], 0.0)

    def test_tag_count_reward(self):
        """Test tag_count_reward with full and partial tags."""
        completions = [
            [{"content": "<think>\nReasoning\n</think>\n<answer>\nSolution\n</answer>"}],
            [{"content": "Reasoning\n</think>\n<answer>\nSolution\n</answer>"}]
        ]
        rewards = tag_count_reward(completions)
        self.assertEqual(rewards[0], 1.0)
        self.assertEqual(rewards[1], 0.75)

    def test_reasoning_steps_reward(self):
        """Test reasoning_steps_reward with varying step counts."""
        completions = [
            [{"content": "Step 1: first\nStep 2: second\nStep 3: third"}],
            [{"content": "Step 1: only step"}]
        ]
        rewards = reasoning_steps_reward(completions)
        self.assertEqual(rewards[0], 1.0)
        self.assertAlmostEqual(rewards[1], 1/3)

    def test_repetition_penalty_reward(self):
        """Test repetition penalty with varying repetition levels."""
        penalty_fn = get_repetition_penalty_reward(ngram_size=2, max_penalty=-1.0)
        completions = [
            [{"content": "this is a test"}],
            [{"content": "this this this this this"}]
        ]
        rewards = penalty_fn(completions)
        self.assertEqual(rewards[0], 0.0)
        self.assertAlmostEqual(rewards[1], -0.75)

    def test_code_format_reward(self):
        """Test code_format_reward with various formatting scenarios."""
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
