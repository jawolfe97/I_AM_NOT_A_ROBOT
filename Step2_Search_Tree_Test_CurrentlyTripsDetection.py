import os
import time
import random

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
list_filename = os.path.join(script_folder, "List.txt")
output_filename = os.path.join(script_folder, "Output.txt")


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


if len(input_lines) < 3:
    raise ValueError(
        "Input.txt must contain at least three lines:\n"
        "Line 1: Target_Link - [Link] (retained for compatibility)\n"
        "Line 2: Link_Search_Pattern - [Substring] (retained for compatibility)\n"
        "Line 3: SubLink_Search_Pattern - [Substring]"
    )


# =========================================================
# 3. EXTRACT SUBLINK SEARCH PATTERN FROM LINE 3
# =========================================================

sub_link_pattern_line = input_lines[2]

if " - " in sub_link_pattern_line:
    sub_link_search_pattern = (
        sub_link_pattern_line.split(" - ", 1)[1].strip()
    )
else:
    sub_link_search_pattern = sub_link_pattern_line.strip()


if not sub_link_search_pattern:
    raise ValueError(
        "SubLink_Search_Pattern is empty in Input.txt line 3."
    )


# =========================================================
# 4. READ LIST.TXT
# =========================================================

if not os.path.exists(list_filename):
    raise FileNotFoundError(
        f"List.txt was not found in the Python script folder:\n"
        f"{script_folder}"
    )

with open(list_filename, "r", encoding="utf-8") as f:
    target_links = [
        line.strip()
        for line in f.readlines()
        if line.strip()
    ]


if not target_links:
    raise ValueError(
        "List.txt does not contain any usable links."
    )


# =========================================================
# 5. DISPLAY SETTINGS
# =========================================================

print()
print("=========================================================")
print("Input Settings")
print("=========================================================")
print(f"List File:            {list_filename}")
print(f"SubLink Search:       {sub_link_search_pattern}")
print(f"Output File:          {output_filename}")
print(f"Links to Process:     {len(target_links)}")
print("=========================================================")
print()


# =========================================================
# 6. LINK ACCESSIBILITY FUNCTION
# =========================================================

def matching_link_is_available(driver):
    """
    Determine whether at least one visible/enabled link
    containing the requested substring is available.
    """

    links = driver.find_elements(
        By.TAG_NAME,
        "a"
    )

    for link in links:

        try:

            # Check that the link is visible
            if not link.is_displayed():
                continue

            # Check that the link is enabled
            if not link.is_enabled():
                continue

            # Get the URL
            url = link.get_attribute("href")

            if not url:
                continue

            # Check whether the URL contains the requested substring
            if sub_link_search_pattern in url:
                return True

        except Exception:
            # The page may be dynamically changing while Selenium
            # is examining the links.
            continue

    return False

##
driver = webdriver.Chrome()
original_tab = driver.current_window_handle
##time.sleep(random.uniform(10.0, 15.0))
##

# =========================================================
# 7. PROCESS EACH LINE OF LIST.TXT
# =========================================================

# Store all matching links from all pages
all_found_links = []

# Statistics
pages_processed = 0
pages_no_matches = 0
pages_failed = 0


for page_number, target_link in enumerate(
    target_links,
    start=1
):

    print()
    print("=========================================================")
    print(
        f"Processing page {page_number} "
        f"of {len(target_links)}"
    )
    print("=========================================================")
    print(f"URL: {target_link}")
    print()

    ##driver = None

    try:

        # =====================================================
        # 8. START CHROME FOR CURRENT PAGE
        # =====================================================

        ##driver = webdriver.Chrome()
        ##driver.get(target_link)
        ##
        driver.switch_to.new_window('tab')
        driver.get(target_link)
        ##


        # =====================================================
        # 9. WAIT FOR PAGE TO LOAD
        # =====================================================

        print("Waiting for the page to become accessible...")
        print()
        print(
            "Pausing for 10 seconds. If an "
            "'I am not a robot' test appears, "
            "complete it."
        )
        print()


        # =====================================================
        # 10. WAIT FOR MATCHING LINK, Exit if not found.
        # =====================================================
        print(
            "The program will automatically continue "
            "when a matching link becomes available."
        )
        print()
        
        WebDriverWait(
            driver,
            10,
            poll_frequency=0.5
        ).until(
            matching_link_is_available
        )


        print("Accessible page detected.")
        print("Matching links are available.")
        print("Beginning link extraction...")
        print()


        # =====================================================
        # 11. FIND ALL ANCHOR TAGS
        # =====================================================
        links = driver.find_elements(
            By.TAG_NAME,
            "a"
        )


        # =====================================================
        # 12. FILTER LINKS
        # =====================================================

        found_links = []

        for link in links:

            try:

                # Only consider links that are visible
                if not link.is_displayed():
                    continue

                # Only consider links that are enabled
                if not link.is_enabled():
                    continue

                # Get the URL
                url = link.get_attribute("href")

                if not url:
                    continue

                # Check whether the URL contains the requested substring
                if sub_link_search_pattern in url:
                    found_links.append(url)

            except Exception:
                # Ignore links that disappear/change while
                # the page is being processed
                continue


        # =====================================================
        # 13. CHECK FOR NO MATCHING LINKS
        # =====================================================

        if not found_links:
        #if found_links == []:

            pages_no_matches += 1

            print()
            print(
                "No relevant links found on this page."
            )
            print(
                "Closing the page and continuing to the "
                "next line of List.txt."
            )
            print()

            continue


        # =====================================================
        # 14. REMOVE DUPLICATES FROM CURRENT PAGE
        # =====================================================

        # Preserve original order
        unique_links = list(
            dict.fromkeys(found_links)
        )


        # =====================================================
        # 15. ADD CURRENT PAGE LINKS TO MASTER LIST
        # =====================================================

        all_found_links.extend(
            unique_links
        )

        pages_processed += 1


        # =====================================================
        # 16. CURRENT PAGE SUMMARY
        # =====================================================

        print("Page extraction complete.")
        print(
            f"Matching links found: {len(found_links)}"
        )
        print(
            f"Unique links found:    {len(unique_links)}"
        )
        print()


    except Exception as e:

        # =====================================================
        # 17. HANDLE PAGE ERRORS
        # =====================================================

        pages_failed += 1

        print()
        print("An error occurred while processing this page:")
        print(
            f"{type(e).__name__}: {e}"
        )
        print()
        print(
            "Skipping to the next line of List.txt."
        )
        print()


    finally:

        # =====================================================
        # 18. CLOSE CURRENT CHROME WINDOW
        # =====================================================

        if driver is not None:

            try:
                ##driver.quit()
                ##
                driver.close()
                driver.switch_to.window(original_tab)
                ##time.sleep(random.uniform(10.0, 15.0))
                ##

            except Exception:
                pass


# =========================================================
# 19. REMOVE DUPLICATES ACROSS ALL PAGES
# =========================================================

unique_all_links = list(
    dict.fromkeys(all_found_links)
)


# =========================================================
# 20. WRITE LINKS TO OUTPUT.TXT
# =========================================================

with open(
    output_filename,
    "w",
    encoding="utf-8"
) as f:

    for url in unique_all_links:
        f.write(url + "\n")


# =========================================================
# 21. FINAL SUMMARY
# =========================================================

##
driver.quit()
##

print()
print("=========================================================")
print("LINK EXTRACTION COMPLETE")
print("=========================================================")
print(
    f"Pages in List.txt:          {len(target_links)}"
)
print(
    f"Pages with relevant links:  {pages_processed}"
)
print(
    f"Pages with no matches:       {pages_no_matches}"
)
print(
    f"Pages with errors:           {pages_failed}"
)
print(
    f"Total matching links found:  {len(all_found_links)}"
)
print(
    f"Unique matching links:       {len(unique_all_links)}"
)
print(
    f"Output file:                 {output_filename}"
)
print("=========================================================")
print()
print("Chrome closed.")
print()
