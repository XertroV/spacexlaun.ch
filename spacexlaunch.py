from flask import Flask, render_template, url_for
from bs4 import BeautifulSoup
import requests
import arrow
import os
import threading
import time

app = Flask(__name__)


wiki_page = "https://en.wikipedia.org/wiki/List_of_Falcon_9_and_Falcon_Heavy_launches"
next_date = ""
update_thread = threading.Thread()


def pr(s):
    print(repr(s))


def refresh_next_date():
    global next_date
    html = requests.get(wiki_page).content
    soup = BeautifulSoup(html, 'html.parser')
    main_content = soup.find(id='mw-content-text')
    found_future_launches = False

    for c in main_content.find_all(['h2', 'table']):
        if c is None: continue
        #print(repr(c))
        if "Future launches" in c.get_text() and c.name == "h2":
            found_future_launches = True
            continue
        if found_future_launches and c.name == 'table':
            e1 = c
            e2 = e1.find_all('tr')[2]
            date_elem = e2.find_all('td')[0]
            pr(date_elem)

            while True:
                try:
                    date_elem.sup.extract()
                except:
                    break

            date_text = date_elem.get_text()
            next_date = arrow.get(date_text, "MMMM D, YYYY")
            try:
                next_date = arrow.get(date_text, "MMMM D, YYYY, HH:mm")
            except:
                pass
            print(next_date)
            break


def update_forever():
    while True:
        refresh_next_date()
        time.sleep(60)


update_thread = threading.Thread(target=update_forever)
update_thread.start()


@app.route("/")
def spacex_template():
    return render_template('index.html', next_date=next_date)


if __name__ == "__main__":
    app.run(port=int(os.environ.get('PORT', 5000)))

    url_for('static', filename='countdown.min.js')
    url_for('static', filename='moment-countdown.min.js')