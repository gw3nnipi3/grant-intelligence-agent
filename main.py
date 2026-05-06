from tools.email_reader import EmailReader
from tools.grant_extractor import GrantExtractor
import csv


# ----------------------------
# EXPORT FUNCTION (CSV → Google Sheets ready)
# ----------------------------
def export_to_csv(all_grants, filename="grants_output.csv"):

    if not all_grants:
        print("⚠️ No grants to export.")
        return

    fields = [
        "title",
        "provider",
        "category",
        "amount",
        "deadline",
        "eligibility",
        "link",
        "confidence",
        "source"
    ]

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()

        for g in all_grants:
            writer.writerow({field: g.get(field, "") for field in fields})

    print(f"\nExported {len(all_grants)} grants → {filename}")


# ----------------------------
# MAIN PIPELINE
# ----------------------------
def run():

    print("Fetching emails.")

    reader = EmailReader()
    emails = reader.fetch_and_process(30)

    print(f"Emails fetched: {len(emails)}")

    extractor = GrantExtractor(model="llama3")

    all_grants = []

    print("\nExtracting grants.\n")

    for i, email in enumerate(emails, start=1):

        body = email.get("body", "")

        if not body or len(body) < 50:
            continue

        print(f"Processing email {i}/{len(emails)}")

        result = extractor.extract_grants(body)

        grants = result.get("grants", [])

        # debug only when needed
        print(f"→ Found {len(grants)} grants")

        for g in grants:

            # safe fallback so nothing crashes
            cleaned = {
                "title": g.get("title", "").strip(),
                "provider": g.get("provider", "").strip(),
                "category": g.get("category", "").strip(),
                "amount": g.get("amount", "").strip(),
                "deadline": g.get("deadline", "").strip(),
                "eligibility": g.get("eligibility", "").strip(),
                "link": g.get("link", "").strip(),
                "confidence": g.get("confidence", 0),
                "source": email.get("email_subject", "unknown")
            }

            # skip empty junk entries
            if not cleaned["title"]:
                continue

            all_grants.append(cleaned)

    # ----------------------------
    # RESULTS OUTPUT
    # ----------------------------
    print("\n================ RESULTS ================\n")

    for g in all_grants:

        print("TITLE:", g["title"])
        print("PROVIDER:", g["provider"])
        print("CATEGORY:", g["category"])
        print("AMOUNT:", g["amount"])
        print("DEADLINE:", g["deadline"])
        print("ELIGIBILITY:", g["eligibility"])
        print("LINK:", g["link"])
        print("CONFIDENCE:", g["confidence"])
        print("SOURCE:", g["source"])
        print("--------------------------------------")

    # ----------------------------
    # EXPORT
    # ----------------------------
    export_to_csv(all_grants)


# ----------------------------
# ENTRY POINT
# ----------------------------
if __name__ == "__main__":
    run()