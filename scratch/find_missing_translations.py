import sys

sys.path.append(r"c:\Users\Admin\Desktop\billing")
try:
    import lang
except Exception as e:
    print(f"Error loading lang: {e}")
    sys.exit(1)

try:
    import screen_reports
except Exception as e:
    print(f"Error loading screen_reports: {e}")
    sys.exit(1)

headers = []
for rpt in screen_reports.REPORTS:
    for col in rpt["cols"]:
        headers.append(col[1])

# Also check other reports names (titles)
titles = [rpt["title"] for rpt in screen_reports.REPORTS]

print("Report titles:")
missing_titles = []
for t in titles:
    if t not in lang.T:
        missing_titles.append(t)
        print(f"  Missing Title: {ascii(t)}")

print("\nReport headers:")
missing_headers = []
for h in headers:
    if h not in lang.T:
        missing_headers.append(h)
        print(f"  Missing Header: {ascii(h)}")

print(f"\nSummary: {len(missing_titles)} missing titles, {len(missing_headers)} missing headers.")
