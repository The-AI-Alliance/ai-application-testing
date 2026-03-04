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
grep -o '"label":"[^"]*"' src/tests/data/*.jsonl | sort | uniq

echo "Unique Labels and Actions:"
grep -o '"label":"[^"]*","actions":"[^"]*"' src/tests/data/*.jsonl | sort | uniq

echo "Missing Labels:"
grep -vn '"label":' src/tests/data/*.jsonl

echo "Missing Actions:"
grep -vn '"actions":' src/tests/data/*.jsonl

echo "Missing Ratings:"
grep -vn '"rating":' src/tests/data/*.jsonl
