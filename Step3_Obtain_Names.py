import os
import requests
import feedparser
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# =========================================================
# SETTINGS
# =========================================================

SCRIPT_FOLDER = os.path.dirname(
    os.path.abspath(__file__)
)

INPUT_FILE = os.path.join(
    SCRIPT_FOLDER,
    "Output.txt"
)

OUTPUT_FILE = os.path.join(
    SCRIPT_FOLDER,
    "Output_Formatted.txt"
)


# =========================================================
# RSC SESSION
# =========================================================

def create_rsc_session():

    session = requests.Session()

    retry_strategy = Retry(
        total=4,
        connect=4,
        read=4,
        status=4,
        status_forcelist=[
            429,
            500,
            502,
            503,
            504
        ],
        allowed_methods=["GET"],
        backoff_factor=1,
        respect_retry_after_header=True
    )

    adapter = HTTPAdapter(
        max_retries=retry_strategy
    )

    session.mount(
        "http://",
        adapter
    )

    session.mount(
        "https://",
        adapter
    )

    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/151.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": (
            "application/rss+xml,"
            "application/xml,"
            "text/xml,"
            "text/html;q=0.9,"
            "*/*;q=0.8"
        ),
        "Connection": "keep-alive"
    })

    return session


# =========================================================
# READ RSC FEED
# =========================================================

def get_rsc_feed_title(feed_url, session):
    """
    Access an RSC RSS feed and return the channel title.

    The URL is used exactly as supplied in Output.txt.
    """

    try:

        response = session.get(
            feed_url,
            headers={
                "Accept": (
                    "application/rss+xml,"
                    "application/xml,"
                    "text/xml,"
                    "*/*;q=0.8"
                ),
                "Referer": "https://pubs.rsc.org/"
            },
            timeout=(20, 60)
        )

        response.raise_for_status()

    except requests.exceptions.RequestException as e:

        print(
            f"ERROR accessing feed:\n"
            f"    {feed_url}\n"
            f"    {e}"
        )

        return None

    # -----------------------------------------------------
    # Parse the RSS XML.
    # -----------------------------------------------------

    feed = feedparser.parse(
        response.content
    )

    # -----------------------------------------------------
    # Extract the channel title.
    # -----------------------------------------------------

    title = feed.feed.get(
        "title",
        ""
    )

    if title:

        return title.strip()

    # -----------------------------------------------------
    # If feedparser does not expose the title, return None.
    # -----------------------------------------------------

    print(
        f"WARNING: No RSS title found:\n"
        f"    {feed_url}"
    )

    return None


# =========================================================
# MAIN
# =========================================================

def main():

    print("=" * 70)
    print("RSC RSS FEED FORMATTER")
    print("=" * 70)

    # -----------------------------------------------------
    # Verify input file.
    # -----------------------------------------------------

    if not os.path.exists(INPUT_FILE):

        print(
            f"\nERROR: Could not find:\n"
            f"{INPUT_FILE}"
        )

        input(
            "\nPress Enter to exit..."
        )

        return

    # -----------------------------------------------------
    # Read URLs from Output.txt.
    # -----------------------------------------------------

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as infile:

        feed_urls = [
            line.strip()
            for line in infile
            if line.strip()
        ]

    print(
        f"\nFound {len(feed_urls)} feed URL(s)."
    )

    # -----------------------------------------------------
    # Create one persistent RSC session.
    # -----------------------------------------------------

    session = create_rsc_session()

    results = []

    # -----------------------------------------------------
    # Process each feed.
    # -----------------------------------------------------

    for number, feed_url in enumerate(
        feed_urls,
        start=1
    ):

        print(
            f"\n[{number}/{len(feed_urls)}]"
        )

        print(
            f"Accessing: {feed_url}"
        )

        title = get_rsc_feed_title(
            feed_url,
            session
        )

        if title:

            line = f"{title} - {feed_url}"

            results.append(line)

            print(
                f"Title: {title}"
            )

        else:

            print(
                "Feed title could not be determined."
            )

    # -----------------------------------------------------
    # Write formatted output.
    # -----------------------------------------------------

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as outfile:

        for line in results:

            outfile.write(
                line + "\n"
            )

    # -----------------------------------------------------
    # Summary.
    # -----------------------------------------------------

    print("\n" + "=" * 70)
    print("COMPLETE")
    print("=" * 70)

    print(
        f"Feeds read:       {len(feed_urls)}"
    )

    print(
        f"Titles obtained:  {len(results)}"
    )

    print(
        f"Output file:      {OUTPUT_FILE}"
    )

    print("=" * 70)

    input(
        "\nPress Enter to exit..."
    )


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    main()
