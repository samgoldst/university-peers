import time
import requests
from bs4 import BeautifulSoup
import html

done = set()
todo = set()


todo.add("https://nces.ed.gov/ipeds/dfr/2024/ReportHTML.aspx?unitId=240444")

with open("institutions.csv", "w", newline="", encoding="utf-8") as institutions_file, \
    open("edges.csv", "w", newline="", encoding="utf-8") as edges_file:

    institutions_file.write("school_id;name;city;peer_type\n")
    edges_file.write("source_id,target_id\n")

    while todo:

        print(f"{len(done):04d} schools done | {len(todo):04d} queued")
        link = todo.pop()

        try:
            response = requests.get(link, timeout=30)
            response.raise_for_status()

            html_page = response.content
            soup = BeautifulSoup(html_page, "lxml")

            if "a group of comparison institutions was selected for you" in soup.get_text(" ", strip=True):
                peer_type = "automatic"
            elif "The custom comparison group chosen by" in soup.get_text(" ", strip=True):
                peer_type = "custom"
            else:
                peer_type = "unknown"

            name = html.unescape(str(soup.find_all("span")[0]).split('\n')[1].split("<br/>")[1])
            city = html.unescape(str(soup.find_all("span")[0]).split('\n')[1].split("<br/>")[2].split("<")[0])

            institutions_file.write(f'{link.split("=")[1]};{name};{city};{peer_type}\n')
            institutions_file.flush()

            for item in soup.find_all("a"):
                if "target" in str(item) and "unitId=" in str(item):
                    new_link = str(item).split('"')[1]
                    edges_file.write(f'{link.split("=")[1]},{new_link.split("=")[1]}\n')
                    edges_file.flush()

                    if new_link not in done:
                        todo.add(new_link)

        except Exception as e:
            print(f"\nFailed: {link}")
            print(e)
            todo.add(link)
            time.sleep(5)
            continue

        # ONLY mark successful pages as done
        done.add(link)

print("\nCompletely Done!")
