import re

LOG_FILE = 'logs/bts_api_pentest.log'
REPORT_FILE = 'reports/summary_report.txt'

def parse_log():
    success_pattern = re.compile(r'\[SUCCESS\] BTS ID (.+) returned location data')
    warn_pattern = re.compile(r'\[WARN\] BTS ID (.+) response missing location field')
    error_pattern = re.compile(r'\[ERROR\] BTS ID (.+)')
    fail_pattern = re.compile(r'\[FAIL\] BTS ID (.+) returned status (\d+)')

    success = []
    warn = []
    error = []
    fail = []

    with open(LOG_FILE, 'r') as f:
        for line in f:
            if success_pattern.search(line):
                bts_id = success_pattern.search(line).group(1)
                success.append(bts_id)
            elif warn_pattern.search(line):
                bts_id = warn_pattern.search(line).group(1)
                warn.append(bts_id)
            elif error_pattern.search(line):
                bts_id = error_pattern.search(line).group(1)
                error.append(bts_id)
            elif fail_pattern.search(line):
                bts_id, status = fail_pattern.search(line).groups()
                fail.append((bts_id, status))

    return success, warn, error, fail

def generate_report():
    success, warn, error, fail = parse_log()

    with open(REPORT_FILE, 'w') as f:
        f.write("=== BTS API Pentest Summary Report ===\n\n")
        f.write(f"Total Successful Responses with Location Data: {len(success)}\n")
        f.write(f"Total Warnings (Missing Location Field): {len(warn)}\n")
        f.write(f"Total Errors (Invalid JSON or No Response): {len(error)}\n")
        f.write(f"Total Failed Requests (Non-200 Status): {len(fail)}\n\n")

        f.write("Successful BTS IDs:\n")
        for bts_id in success:
            f.write(f" - {bts_id}\n")

        f.write("\nWarnings BTS IDs:\n")
        for bts_id in warn:
            f.write(f" - {bts_id}\n")

        f.write("\nErrors BTS IDs:\n")
        for bts_id in error:
            f.write(f" - {bts_id}\n")

        f.write("\nFailed Requests (BTS ID and Status Code):\n")
        for bts_id, status in fail:
            f.write(f" - {bts_id}: {status}\n")

    print(f"Summary report generated at {REPORT_FILE}")

if __name__ == "__main__":
    generate_report()
