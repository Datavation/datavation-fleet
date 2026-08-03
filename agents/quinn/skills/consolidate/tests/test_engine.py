"""pytest wrapper — re-exposes the dependency-light self-test functions so
`pytest` discovers them too. The canonical runner is `python tests/run_selftest.py`.
"""

from tests.run_selftest import (  # noqa: F401
    test_no_network_imports,
    test_money,
    test_dates,
    test_redaction,
    test_barclaycard_parse_and_tieout_good,
    test_barclaycard_tieout_bad_flags,
    test_mortgage_parse,
    test_mortgage_tieout_warns,
    test_quickbooks_adapter_parse,
    test_quickbooks_split_lines_survive_dedup,
    test_end_to_end,
    test_determinism,
    test_custodial_excluded,
    test_manual_lines_net_worth_rollup,
    test_init_creates_rules_skeleton,
    test_run_without_rules_fails_loud_not_silent,
    test_template_emits_clean_bundle,
)
