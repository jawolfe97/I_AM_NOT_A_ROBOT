import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


# =========================================================
# 1. FILE LOCATIONS
# =========================================================

# Get the folder containing this Python script
script_folder = os.path.dirname(os.path.abspath(__file__))

# Input and output files
input_filename = os.path.join(script_folder, "Input.txt")
output_filename = os.path.join(script_folder, "List.txt")


# =========================================================
# 2. READ INPUT.TXT
# =========================================================

if not os.path.exists(input_filename):
    raise FileNotFoundError(
        f"Input.txt was not found in the Python script folder:\n"
        f"{script_folder}"
    )


with open(input_filename, "r", encoding="utf-8") as f:
    input_lines = [line.strip() for line in f.readlines()]


if len(input_lines) < 2:
    raise ValueError(
        "Input.txt must contain at least two lines:\n"
        "Line 1: Target_Link - [Link]\n"
        "Line 2: Link_Search_Pattern - [Substring]"
    )


# =========================================================
# 3. EXTRACT TARGET LINK
# =========================================================

target_line = input_lines[0]

if " - " in target_line:
    target_link = target_line.split(" - ", 1)[1].strip()
else:
    target_link = target_line.strip()


# =========================================================
# 4. EXTRACT LINK SEARCH PATTERN
# =========================================================

pattern_line = input_lines[1]

if " - " in pattern_line:
    link_search_pattern = pattern_line.split(" - ", 1)[1].strip()
else:
    link_search_pattern = pattern_line.strip()


if not target_link:
    raise ValueError(
        "Target_Link is empty in Input.txt"
    )


if not link_search_pattern:
    raise ValueError(
        "Link_Search_Pattern is empty in Input.txt"
    )


# =========================================================
# 5. DISPLAY SETTINGS
# =========================================================

print()
print("=========================================================")
print("Input Settings")
print("=========================================================")
print(f"Target Link:          {target_link}")
print(f"Link Search Pattern:  {link_search_pattern}")
print(f"Output File:          {output_filename}")
print("=========================================================")
print()


# =========================================================
# 6. START CHROME
# =========================================================

driver = webdriver.Chrome()

driver.get(target_link)


# =========================================================
# 7. WAIT FOR PAGE TO BECOME ACCESSIBLE
# =========================================================

print("Waiting for the page to become accessible...")
print()
time.sleep(10)
print("Pausing for 10 seconds. If an 'I am not a robot' test appears, complete it.")
print("The program will automatically continue when a")
print("matching link becomes available.")
print()



def matching_link_is_available(driver):

    links = driver.find_elements(By.TAG_NAME, "a")

    for link in links:

        try:
            # Check that the link is visible and enabled
            if not link.is_displayed():
                continue

            if not link.is_enabled():
                continue

            # Get the URL
            url = link.get_attribute("href")

            if not url:
                continue

            # Check whether the URL contains the required substring
            if link_search_pattern in url:
                return True

        except Exception:
            # The page may be dynamically changing while Selenium
            # is examining the links. Ignore an individual link
            # that disappears during this process.
            continue

    return False


# Wait up to 120 seconds for at least one matching link
WebDriverWait(driver, 120, poll_frequency=0.5).until(
    matching_link_is_available
)



print("Accessible page detected.")
print("Matching links are available.")
print("Beginning link extraction...")
print()


# =========================================================
# 8. FIND ALL ANCHOR TAGS
# =========================================================

links = driver.find_elements(By.TAG_NAME, "a")


# =========================================================
# 9. FILTER LINKS
# =========================================================

found_links = []

for link in links:

    try:

        # Only consider links that are visible and enabled
        if not link.is_displayed():
            continue

        if not link.is_enabled():
            continue

        # Get the URL
        url = link.get_attribute("href")

        if not url:
            continue

        # Check whether the URL contains the requested substring
        if link_search_pattern in url:
            found_links.append(url)

    except Exception:
        # Ignore links that disappear/change while the page
        # is being processed
        continue


# =========================================================
# 10. REMOVE DUPLICATE LINKS
# =========================================================

# Preserve the original order while removing duplicates
unique_links = list(dict.fromkeys(found_links))


# =========================================================
# 11. WRITE LINKS TO LIST.TXT
# =========================================================

with open(output_filename, "w", encoding="utf-8") as f:

    for url in unique_links:
        f.write(url + "\n")


# =========================================================
# 12. SUMMARY
# =========================================================

print()
print("=========================================================")
print("Link Extraction Complete")
print("=========================================================")
print(f"Links found:       {len(found_links)}")
print(f"Unique links:      {len(unique_links)}")
print(f"Output file:       {output_filename}")
print("=========================================================")
print()


# =========================================================
# 13. QUIT DRIVER
# =========================================================

driver.quit()
