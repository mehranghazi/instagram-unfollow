A robust and automated Python script built with Playwright to safely unfollow Instagram users who don't follow you back. This tool simulates real human interactions in the browser, minimizing the risk of triggering Instagram's anti-bot protections.

## Features
- **Session Persistence:** Saves your login session so you only need to log in once.
- **Human-like Behavior:** Uses randomized delays (4 to 8 seconds) between actions.
- **Robust DOM Handling:** Dynamically locates buttons and handles UI changes.
- **Detailed Logging:** Generates a `results.csv` file.
- **CSV Driven:** Feed the script a list of targets using a simple CSV file.

## Prerequisites
- Python 3.8+
- Google Chrome installed on your system

## Installation
1. Clone the repository:
   ```bash
   git clone [https://github.com/mehranghazi/instagram-unfollow.git](https://github.com/mehranghazi/instagram-unfollow.git)
   cd instagram-unfollow


2. Install the required Python packages:
   pip install -r requirements.txt
   
3. Install Playwright browser binaries:
   playwright install chromium
   

How to Use

1. Prepare the Target List:
   You must provide a CSV file named batch.csv in the root folder. The file must have username as the column header in the first line, followed by the target accounts on each new line. You can use the included sample_batch.csv as a template.

   Example of batch.csv:

   username
   target_account_1
   target_account_2
   
2. Run the Script:
   python instagram_unfollow.py
   
3. First-Time Setup: A browser will open. Log in manually. Your session saves in instagram_browser_profile/. Go back to the terminal and press ENTER.

Disclaimer

For educational purposes only. Automating actions on Instagram is against their Terms of Service. Use at your own risk.
