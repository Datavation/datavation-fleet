"""Synthetic fixture: a self-test that always fails. Used only to prove qa_verify.py
correctly recognises a FAIL, and does not launder a broken build into a PASS. Not a real build."""
import sys

print("fixture failing_build: 2/3 checks OK, 1 FAILED (deliberate)")
sys.exit(1)
