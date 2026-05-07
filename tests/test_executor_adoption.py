from pathlib import Path

import yaml


def test_executor_policy_contract_is_fixture_safe():
    policy = yaml.safe_load(Path("executor.policy.yaml").read_text())
    assert policy["schema"] == "workflow-proof-executor-policy/v1"
    assert policy["namespace"] == "automation_kit"
    assert policy["fixture_safe"] is True
    assert policy["live_services_used"] is False
    assert policy["reads"]["default"] == "allow"
    assert policy["writes"]["default"] == "require_operator_approval"
    assert policy["auth"]["required"] is False
    assert policy["smoke"]["health_url"].startswith("http://127.0.0.1:")
