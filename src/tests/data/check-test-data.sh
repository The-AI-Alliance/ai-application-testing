#!/usr/bin/env zsh

# Check the JSONL data files.

# for file in src/tests/data/*.jsonl
# do
# 	echo
# 	echo "File: $file"
# 	echo "Unique Labels:"
# 	grep -o '"label":"[^"]*"' $file | sort | uniq

# 	echo "Unique Labels and Actions:"
# 	grep -o '"label":"[^"]*","actions":"[^"]*"' $file | sort | uniq
# done

echo "Unique Labels:"
jq -c '{label}' src/tests/data/*.jsonl | sort | uniq

echo "Unique Labels and Actions:"
jq -c '{label, actions}' src/tests/data/*.jsonl | sort | uniq

echo "Checking for missing fields. NOTE: blank lines will be reported!"
echo "e.g., 'src/tests/data/appointments.jsonl:10:' (note nothing after the 'number:')"

echo "Missing Labels:"
grep -vn '"label":' src/tests/data/*.jsonl

echo "Missing Actions:"
grep -vn '"actions":' src/tests/data/*.jsonl

echo "Missing Ratings:"
grep -vn '"rating":' src/tests/data/*.jsonl
