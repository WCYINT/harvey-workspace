# text-diff

Show line-by-line differences between two text files using Python's difflib.

## Description

A utility skill for comparing two text files and displaying their differences in a readable format. Supports unified diff output and side-by-side comparison modes.

## Usage

```bash
# Show unified diff between two files
python ~/.openclaw/skills/text-diff/text_diff.py unified file1.txt file2.txt

# Show side-by-side comparison
python ~/.openclaw/skills/text-diff/text_diff.py side-by-side file1.txt file2.txt

# Show context diff (3 lines of context)
python ~/.openclaw/skills/text-diff/text_diff.py context file1.txt file2.txt

# Compare with custom context lines
python ~/.openclaw/skills/text-diff/text_diff.py unified file1.txt file2.txt -c 5
```

## Options

- `unified`: Show unified diff format (default)
- `context`: Show context diff format
- `side-by-side`: Show line-by-line comparison
- `-c, --context`: Number of context lines (default: 3)
- `-o, --output`: Save diff to file instead of stdout
- `--no-color`: Disable colored output

## Examples

```bash
# Basic unified diff
python ~/.openclaw/skills/text-diff/text_diff.py unified old.txt new.txt

# Side-by-side comparison with no colors (for piping)
python ~/.openclaw/skills/text-diff/text_diff.py side-by-side old.txt new.txt --no-color

# Save diff to file
python ~/.openclaw/skills/text-diff/text_diff.py unified old.txt new.txt -o diff.txt

# Compare with 10 lines of context
python ~/.openclaw/skills/text-diff/text_diff.py context old.txt new.txt -c 10
```

## Output Format

### Unified Diff
```
--- old.txt
+++ new.txt
@@ -1,5 +1,5 @@
 line 1
 line 2
-line 3 (removed)
+line 3 (added)
 line 4
 line 5
```

### Side-by-Side
```
OLD                          | NEW
---------------------------- | ----------------------------
line 1                       | line 1
line 2                       | line 2
line 3 (removed)             | line 3 (added)
line 4                       | line 4
```

## Exit Codes

- `0`: Files are identical
- `1`: Files differ
- `