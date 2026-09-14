import csv
import random
import time
from pathlib import Path

import pandas as pd
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

CSV_FILE = Path("batch.csv")
RESULTS_FILE = Path("results.csv")

MIN_DELAY = 4
MAX_DELAY = 8


def load_usernames():
    df = pd.read_csv(CSV_FILE)

    if "username" not in df.columns:
        raise ValueError(
            f"CSV must contain a 'username' column. Found: {list(df.columns)}"
        )

    usernames = (
        df["username"]
        .dropna()
        .astype(str)
        .str.strip()
        .str.lstrip("@")
    )

    return list(dict.fromkeys(
        u for u in usernames
        if u and u.lower() != "nan"
    ))


def save_result(username, status, reason, url):
    exists = RESULTS_FILE.exists()

    with RESULTS_FILE.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["username", "status", "reason", "url"]
        )

        if not exists:
            writer.writeheader()

        writer.writerow({
            "username": username,
            "status": status,
            "reason": reason,
            "url": url
        })


def get_following_button(page):
    buttons = page.get_by_role("button")

    for i in range(min(buttons.count(), 40)):
        try:
            text = buttons.nth(i).inner_text().strip().lower()

            if text == "following" or text.startswith("following "):
                return buttons.nth(i)

        except Exception:
            pass

    return None


def unfollow_user(page, username):
    url = f"https://www.instagram.com/{username}/"

    print(f"\n@{username}")
    print("  Opening profile...")

    try:
        page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=30000
        )

        page.wait_for_timeout(2500)

        body = page.locator("body").inner_text(timeout=10000).lower()

        if "something went wrong" in body:
            return "ERROR", "something_went_wrong"

        if (
            "sorry, this page isn't available" in body
            or "page isn't available" in body
            or "user not found" in body
        ):
            return "PROFILE_UNAVAILABLE", "profile_not_available"

        following_button = get_following_button(page)

        if following_button is None:
            return "NOT_FOLLOWING", "following_button_not_found"

        print("  Following button found.")
        print("  Clicking Following...")

        following_button.click()

        page.wait_for_timeout(1000)

        # Instagram normally opens a confirmation menu/dialog.
        # Find the Unfollow action without relying on a fixed DOM selector.
        unfollow = page.get_by_text("Unfollow", exact=True)

        if unfollow.count() == 0:
            return "ERROR", "unfollow_confirmation_not_found"

        print("  Clicking Unfollow...")

        unfollow.last.click()

        page.wait_for_timeout(2000)

        # Verify: the profile should now expose Follow rather than Following.
        body_after = page.locator("body").inner_text(timeout=10000).lower()

        following_after = get_following_button(page)

        if following_after is not None:
            return "ERROR", "still_following_after_click"

        if "follow" in body_after:
            return "UNFOLLOWED", "unfollow_confirmed"

        return "UNFOLLOWED", "unfollow_clicked"

    except PlaywrightTimeoutError:
        return "ERROR", "page_timeout"

    except Exception as e:
        return "ERROR", type(e).__name__


def main():
    usernames = load_usernames()

    print(f"Loaded {len(usernames)} unique usernames.")
    print("MODE = REAL UNFOLLOW")
    print()

    with sync_playwright() as p:

        context = p.chromium.launch_persistent_context(
            user_data_dir="instagram_browser_profile",
            headless=False,
            executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            viewport={"width": 1280, "height": 900},
        )

        page = context.pages[0] if context.pages else context.new_page()

        page.goto(
            "https://www.instagram.com/",
            wait_until="domcontentloaded"
        )

        print("Browser opened.")
        print("Make sure you are logged into the correct Instagram account.")
        input("When ready, press ENTER to start REAL UNFOLLOW...")

        for index, username in enumerate(usernames, start=1):

            print(f"\n[{index}/{len(usernames)}]")

            url = f"https://www.instagram.com/{username}/"

            status, reason = unfollow_user(page, username)

            print(f"  RESULT: {status}")
            print(f"  REASON: {reason}")

            save_result(
                username,
                status,
                reason,
                url
            )

            if status == "ERROR":
                print("  Error encountered. Waiting before next account.")

            delay = random.uniform(MIN_DELAY, MAX_DELAY)
            print(f"  Waiting {delay:.1f}s...")
            time.sleep(delay)

        context.close()

    print("\nFinished.")
    print(f"Results saved to: {RESULTS_FILE}")


if __name__ == "__main__":
    main()
