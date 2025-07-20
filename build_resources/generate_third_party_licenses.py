"""
Automatically generate a third-party licenses file.
"""
from collections import defaultdict
import hashlib
import json
import os
import subprocess


def hash_license(text):
    """
    Hash the license
    """

    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def run_pip_licenses():
    """
    Run pip licenses
    """

    result = subprocess.run(
        [
            "pip-licenses",
            "--from=mixed",
            "--format=json",
            "--with-license-file",
            "--with-authors",
            "--with-urls"
        ],
        stdout=subprocess.PIPE,
        check=True,
        text=True
    )
    return json.loads(result.stdout)


def group_license(licenses):
    """
    Group by license content
    """

    print("[*] Grouping packages by license content...")
    grouped_licenses = defaultdict(list)

    for pkg in licenses:
        license_text = pkg.get("LicenseFile", "").strip()
        if not license_text:
            print(f"[!] No license file found for: {pkg['Name']}")
            continue

        key = hash_license(license_text)
        grouped_licenses[key].append((
            pkg["Name"],
            pkg["License"],
            pkg["Author"],
            pkg["URL"],
            license_text
        ))

    print(f"[+] Grouped into {len(grouped_licenses)} unique license block(s).")
    return grouped_licenses


def write_deduplicated(grouped_licenses, output_file="THIRD_PARTY_LICENSES.txt"):
    """
    Write licenses to output file
    """
    print(f"[*] Writing deduplicated license report to {output_file}...")
    count = 0

    with open(output_file, "w", encoding="utf-8") as f:
        for i, (_hash_key, group) in enumerate(grouped_licenses.items(), 1):
            names = [name for name, *_ in group]
            license_type = group[0][1]
            authors = set(a for _, _, a, *_ in group if a)
            urls = set(u for _, _, _, u, *_ in group if u)
            license_link = group[0][-1]

            if os.path.isfile(license_link):
                with open(license_link, "r", encoding="utf-8") as t:
                    license_text = t.read().strip()
            else:
                license_text = license_link

            f.write("=" * 80 + "\n")
            f.write(f"License Group #{i}\n")
            f.write(f"License Type: {license_type}\n")
            f.write(f"Used by: {', '.join(sorted(names))}\n")
            if authors:
                f.write(f"Authors: {', '.join(sorted(authors))}\n")
            if urls:
                f.write(f"URLs: {', '.join(sorted(urls))}\n")
            f.write("\n")
            f.write(license_text)
            f.write("\n\n")
            count += 1

    print(f"[+] Successfully wrote {count} license block(s) to {output_file}.")


def generate_third_party_licenses():
    """
    Generate third-party license file
    """

    print("[*] Generating third-party license file...")
    raw_licenses = run_pip_licenses()
    write_deduplicated(group_license(raw_licenses))
    print("[✓] Done.")


if __name__ == "__main__":
    generate_third_party_licenses()
