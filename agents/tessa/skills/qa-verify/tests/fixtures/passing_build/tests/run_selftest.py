"""Synthetic fixture: a self-test that always passes. Used only to prove qa_verify.py
correctly recognises a PASS, both in place and from a clean copy. Not a real build."""
import sys

print("fixture passing_build: 3/3 checks OK")
sys.exit(0)
