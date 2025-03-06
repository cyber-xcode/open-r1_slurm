import json 
from unittest.mock import patch, MagicMock
import pytest
import unittest
import os
import requests
# from reward_functions.remote_rewards import (
from open_r1.rewards import (
    # request_auto,
    reward_asserty_p_check_assert_syntax , 
    reward_asserty_p_is_cheating , 
    reward_asserty_verify, 
    
)

# Sample completions for testing
COMPLETIONS_SAMPLES = [
    [{"content": "```#include <stdio.h>\nint main() { printf(\"Hello, World!\\n\"); return 0; }```"}],
    [{"content": "```#include <stdio.h>\nint main() { for(int i = 0; i < 10; i++) printf(\"%d\\n\", i); return 0; }```"}],
    [{"content": "```#include <stdio.h>\nint main() { printf(\"Missing semicolon\") return 0; }```"}],
]

class TestRemoteRewards(unittest.TestCase):


    def test_remote_check_syntax(self):
        """Test remote_check_syntax with valid and invalid syntax."""
        completions = [
            [{"content": """```#include <stdio.h>\nint main() { printf("Hello, World!\\n"); return 0; }```"""}],
            [{"content": """```#include <stdio.h>\nint main() { printf("Missing semicolon") return 0; }```"""}],
    [{"content": """```assert (a==2); ```"""}],
    [{"content": """```assert (a==2) ```"""}],


        ]
        rewards = reward_asserty_p_check_assert_syntax(completions)
        self.assertEqual(len(rewards), 4)
        self.assertEqual(rewards[0], 0.0)  # Valid syntax
        self.assertEqual(rewards[1], 0.0)   # Invalid syntax
        self.assertEqual(rewards[2], 1.0)   # Invalid syntax
        self.assertEqual(rewards[3], 0.0)   # Invalid syntax


    def test_remote_check_is_cheating(self):
        """Test remote_check_is_cheating with cheating assert."""
        completions = [[{"content": """```
    assert(a == 1);   // valid
    assert(5 == 5);   // cheating: no context
        ```"""}]]
        sourc_code = ["""
#include <assert.h>
int main() {
    int a = 1, b = 2;
    return 0;
}
"""            
            ]
        rewards = reward_asserty_p_is_cheating(completions, source_code= sourc_code )
        self.assertEqual(len(rewards), 1)
        self.assertEqual(rewards[0], 1.0)  # Indicates cheating detected

    def test_reward_asserty_verify(self):
        """Test reward_asserty_verify with successful verification."""
        completions = [COMPLETIONS_SAMPLES[0]]
        with pytest.raises(Exception):
            rewards = reward_asserty_verify(completions, property="unreach-call")
            
        with pytest.raises(Exception):
            rewards = reward_asserty_verify(completions,source_code=completions,  property="unreach-call")
            self.assertEqual(len(rewards), 1)
            self.assertEqual(rewards[0], 1.0)




class TestRewardFunctions(unittest.TestCase):

    @patch('open_r1.rewards.requests.post')
    def test_reward_asserty_p_check_assert_syntax_valid_assert(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"p_check_assert_syntax": 1.0}
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        completions = [[{"content": "```python\nassert x == y\n```"}]]
        result = reward_asserty_p_check_assert_syntax(completions)
        self.assertEqual(result, [1.0])

    @patch('open_r1.rewards.requests.post')
    def test_reward_asserty_p_check_assert_syntax_invalid_assert(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"p_check_assert_syntax": 0.0}
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        completions = [[{"content": "```python\nasert x == y\n```"}]]
        result = reward_asserty_p_check_assert_syntax(completions)
        self.assertEqual(result, [0.0])

    @patch('open_r1.rewards.requests.post')
    def test_reward_asserty_p_check_assert_syntax_no_assert(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"p_check_assert_syntax": 0.5}
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        completions = [[{"content": "```python\nx = y\n```"}]]
        result = reward_asserty_p_check_assert_syntax(completions)
        self.assertEqual(result, [0.5])

    @patch('open_r1.rewards.requests.post')
    def test_reward_asserty_p_check_assert_syntax_multiple_asserts(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"p_check_assert_syntax": 0.8}
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        completions = [[{"content": "```python\nassert x == y\nassert a == b\n```"}]]
        result = reward_asserty_p_check_assert_syntax(completions)
        self.assertEqual(result, [0.8])

    @patch('open_r1.rewards.requests.post')
    def test_reward_asserty_p_check_assert_syntax_empty_code(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"p_check_assert_syntax": 0.0}
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        completions = [[{"content": "```python\n```"}]]
        result = reward_asserty_p_check_assert_syntax(completions)
        print ("result", result )
        self.assertEqual(result, [0.0])

        completions = [[{"content": "```python\n```"}]]
        result = reward_asserty_p_check_assert_syntax(completions)
        self.assertEqual(result, [0.0])


    @patch('open_r1.rewards.requests.post')
    def test_reward_asserty_p_is_cheating_no_cheating(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"p_is_cheating": 0.0}
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        completions = [[{"content": "```python\nassert x == y\n```"}]]
        result = reward_asserty_p_is_cheating(completions,source_code = [""] )
        self.assertEqual(result, [0.0])

    @patch('open_r1.rewards.requests.post')
    def test_reward_asserty_p_is_cheating_cheating_detected(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"p_is_cheating": 1.0}
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        completions = [[{"content": "```python\nassert x == x\n```"}]]
        result = reward_asserty_p_is_cheating(completions,source_code = [""] )
        self.assertEqual(result, [1.0])

    @patch('open_r1.rewards.requests.post')
    def test_reward_asserty_p_is_cheating_partial_cheating(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"p_is_cheating": 0.5}
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        completions = [[{"content": "```python\nassert x == y\nassert a == a\n```"}]]
        result = reward_asserty_p_is_cheating(completions,source_code = [""] )
        self.assertEqual(result, [0.5])

    @patch('open_r1.rewards.requests.post')
    def test_reward_asserty_p_is_cheating_empty_code(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"p_is_cheating": 0.0}
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        completions = [[{"content": "```python\n```"}]]
        result = reward_asserty_p_is_cheating(completions)
        self.assertEqual(result, [0.0])

    @patch('open_r1.rewards.requests.post')
    def test_reward_asserty_p_is_cheating_complex_code(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"p_is_cheating": 0.0}
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        completions = [[{"content": "```python\nif x == y:\n    assert a == b\n```"}]]
        result = reward_asserty_p_is_cheating(completions)
        self.assertEqual(result, [0.0])

    @patch('open_r1.rewards.requests.post')
    def test_reward_asserty_verify_successful_verification(self, mock_post):
        def side_effect(*args, **kwargs):
            if 'p_insert_invariant_from_clangindex' in args[0]:
                return MagicMock(json=lambda: {"p_insert_invariant_from_clangindex": "modified_code"})
            elif 'rewrite' in args[0]:
                return MagicMock(json=lambda: {"new_code": "rewritten_code"})
            elif 'lemur_verifier_with_prop' in args[0]:
                return MagicMock(json=lambda: {"status": 1})
            return None

        mock_post.side_effect = side_effect

        completions = [[{"content": "```python\nassert x == y\n```"}]]
        source_code = ["def foo():\n    pass"]
        result = reward_asserty_verify(completions, source_code=source_code, property="unreach-call")
        self.assertEqual(result, [1.0])


    @patch('open_r1.rewards.requests.post')
    def test_reward_asserty_verify_verification_failure(self, mock_post):
        # Mock responses for verification failure
        def side_effect(*args, **kwargs):
            if 'p_insert_invariant_from_clangindex' in args[0]:
                return MagicMock(json=lambda: {"p_insert_invariant_from_clangindex": "modified_code"})
            elif 'rewrite' in args[0]:
                return MagicMock(json=lambda: {"new_code": "rewritten_code"})
            elif 'lemur_verifier_with_prop' in args[0]:
                return MagicMock(json=lambda: {"status": 2})
            return None

        mock_post.side_effect = side_effect

        completions = [[{"content": "```python\nassert x == y\n```"}]]
        source_code = ["def foo():\n    pass"]
        result = reward_asserty_verify(completions, source_code=source_code, property="unreach-call")
        self.assertEqual(result, [0.0])

    @patch('open_r1.rewards.requests.post')
    def test_reward_asserty_verify_verification_unknown_error(self, mock_post):
        # Mock responses for unknown verification error
        def side_effect(*args, **kwargs):
            if 'p_insert_invariant_from_clangindex' in args[0]:
                return MagicMock(json=lambda: {"p_insert_invariant_from_clangindex": "modified_code"})
            elif 'rewrite' in args[0]:
                return MagicMock(json=lambda: {"new_code": "rewritten_code"})
            elif 'lemur_verifier_with_prop' in args[0]:
                return MagicMock(json=lambda: {"status": 3})
            return None

        mock_post.side_effect = side_effect

        completions = [[{"content": "```python\nassert x == y\n```"}]]
        source_code = ["def foo():\n    pass"]
        result = reward_asserty_verify(completions, source_code=source_code, property="unreach-call")
        self.assertEqual(result, [0.2])

    @patch('open_r1.rewards.requests.post')
    def test_reward_asserty_verify_verification_timeout(self, mock_post):
        # Mock responses for verification timeout
        def side_effect(*args, **kwargs):
            if 'p_insert_invariant_from_clangindex' in args[0]:
                return MagicMock(json=lambda: {"p_insert_invariant_from_clangindex": "modified_code"})
            elif 'rewrite' in args[0]:
                return MagicMock(json=lambda: {"new_code": "rewritten_code"})
            elif 'lemur_verifier_with_prop' in args[0]:
                return MagicMock(json=lambda: {"status": 4})
            return None

        mock_post.side_effect = side_effect

        completions = [[{"content": "```python\nassert x == y\n```"}]]
        source_code = ["def foo():\n    pass"]
        result = reward_asserty_verify(completions, source_code=source_code, property="unreach-call")
        self.assertEqual(result, [0.5])

    @patch('open_r1.rewards.requests.post')
    def test_reward_asserty_verify_no_invariant_inserted(self, mock_post):
        # Mock responses for no invariant inserted
        def side_effect(*args, **kwargs):
            if 'p_insert_invariant_from_clangindex' in args[0]:
                return MagicMock(json=lambda: {"p_insert_invariant_from_clangindex": None})
            return None

        mock_post.side_effect = side_effect

        completions = [[{"content": "```python\nassert x == y\n```"}]]
        source_code = ["def foo():\n    pass"]
        result = reward_asserty_verify(completions, source_code=source_code, property="unreach-call")
        self.assertEqual(result, [0.0])

    @patch('open_r1.rewards.requests.post')
    def test_reward_asserty_verify_multiple_completions(self, mock_post):
        # Mock responses for multiple completions
        def side_effect(*args, **kwargs):
            if 'p_insert_invariant_from_clangindex' in args[0]:
                return MagicMock(json=lambda: {"p_insert_invariant_from_clangindex": "modified_code"})
            elif 'rewrite' in args[0]:
                return MagicMock(json=lambda: {"new_code": "rewritten_code"})
            elif 'lemur_verifier_with_prop' in args[0]:
                return MagicMock(json=lambda: {"status": 1})
            return None

        mock_post.side_effect = side_effect

        completions = [
            [{"content": "```python\nassert x == y\n```"}],
            [{"content": "```python\nassert a == b\n```"}]
        ]
        source_code = ["def foo():\n    pass", "def bar():\n    pass"]
        result = reward_asserty_verify(completions, source_code=source_code, property="unreach-call")
        self.assertEqual(result, [1.0, 1.0])


invriant_raw_c_code='''
#include <stdio.h>
#include <assert.h>

int main() {
    int sum = 0;
    int n = 10;
    int i = 0;

    for (i = 0; i <= n; i++) {
        sum += i;
    }
    return 0;
}

'''
# invriant_raw_c_code = invriant_raw_c_code.encode()

invriant_c_code="assert(sum == (i * (i + 1)) / 2);"

class TestRewardFunctions(unittest.TestCase):

    def test_reward_asserty_p_check_assert_syntax_valid_assert(self):
        completions = [[{"content": "```python\nassert x == y\n```"}]]
        result = reward_asserty_p_check_assert_syntax(completions)
        self.assertEqual(result, [0.0])
        
        completions = [[{"content": "```c\nassert (x == y);\n```"}]]
        result = reward_asserty_p_check_assert_syntax(completions)
        self.assertEqual(result, [1.0])

    def test_reward_asserty_p_is_cheating_no_cheating(self):
        completions = [[{"content": "```python\nassert x == y\n```"}]]
        result = reward_asserty_p_is_cheating(completions)
        self.assertEqual(result, [0.0])

    def test_reward_asserty_verify_successful_verification2(self):
        completions = [[{"content": "```python\nassert x == y\n```"}]]
        source_code = ["def foo():\n    pass"]
        result = reward_asserty_verify(completions, source_code=source_code, property="unreach-call")
        self.assertEqual(result, [0.1])

        completions = [[{"content": f"```c\n{invriant_c_code}\n```"}]]
        source_code = [invriant_raw_c_code]
        result = reward_asserty_verify(completions, source_code=source_code, property="termination")
        self.assertEqual(result, [1.0])

        completions = [[{"content": f"```c\n assert(sum == (i * (i + 1)) / 3); \n```"}]]
        source_code = [invriant_raw_c_code]
        result = reward_asserty_verify(completions, source_code=source_code, property="unreach-call")
        self.assertEqual(result, [0.0])


if __name__ == "__main__":
    unittest.main()
