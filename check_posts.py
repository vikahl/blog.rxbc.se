import datetime
import re
import subprocess
import os

# Get added files in current branch
added_files = subprocess.run(
    ["git", "diff", "--name-only", "--diff-filter=A", "origin/main", "HEAD"],
    encoding="utf-8",
    stdout=subprocess.PIPE,
    check=True,
).stdout


for filename in added_files.split("\n"):
    if filename.startswith("content/posts/"):
        with open(filename) as fh:
            # Ugly, but easy. Rather than creating some clever regex that will
            # only match the metdata within "---" and "---", just read the
            # first 10 lines and be happy with it.
            metadata_block = "".join([next(fh) for _ in range(10)])

            metadata = re.findall("(\w+):\s*(.*)", metadata_block, flags=re.M)

        for line in metadata:
            key, value = line

            # checks
            if key == "draft" and value.lower() == "true":
                raise RuntimeError(
                    "Draft is enabled. It should be disabled before merge!"
                )

            if key == "date":
                # Try to load it as a datetime:
                date = datetime.datetime.fromisoformat(value)

                if datetime.date.today() != date.date():
                    raise RuntimeError(f"Date is too old: {date.date()}. (today {datetime.date.today()})")
