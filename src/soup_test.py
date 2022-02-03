import bs4

with open("test_doc.html", "r") as f:
    markup = f.read()

soup = bs4.BeautifulSoup(markup, "html.parser")

tag = soup.find_all(tag="wind")
print(tag)
tag[0].string = "NEw text guys"
print(soup)

test_workout = [["Thursday", "Reps:", "5"], ["FS", "210x5", "MP"], ["", "325", "245x5"]]
max_width = 0

table = soup.new_tag("table")

for row in test_workout:
    tr = soup.new_tag("tr")
    for col in row:
        td = soup.new_tag("td")
        td.string = col
        tr.append(td)
    table.append(tr)

print(table)
