#!/usr/bin/env zsh

# Check the JSONL data files.

# for file in src/tests/data/*-qna.jsonl
# do
# 	echo
# 	echo "File: $file"
# 	echo "Unique Labels:"
# 	grep -o '"label":"[^"]*"' $file | sort | uniq

# 	echo "Unique Labels and Actions:"
# 	grep -o '"label":"[^"]*","actions":"[^"]*"' $file | sort | uniq
# done

# TODO: Add checks for the scenario tests.

echo "Unique Labels:"
jq -c '{labels}' src/tests/data/*-qna.jsonl | sort | uniq

echo "Unique Labels and Actions:"
jq -c '{labels, actions}' src/tests/data/*-qna.jsonl | sort | uniq

echo "Checking for missing fields. NOTE: blank lines will be reported!"
echo "e.g., 'src/tests/data/appointments-qna.jsonl:10:' (note nothing after the 'number:')"

echo "Missing Labels:"
grep -vn '"labels":' src/tests/data/*-qna.jsonl

echo "Missing Actions:"
grep -vn '"actions":' src/tests/data/*-qna.jsonl

echo "Missing Ratings:"
grep -vn '"rating":' src/tests/data/*-qna.jsonl
