import app as app
import csv  # to read input file
import elicited_information as elicited_info

# read source data (elicited information)
# the csv file contains two columns: source and elicited information text
csv_file = open('elicited_information.csv', 'r')
csv_reader = csv.reader(csv_file)

elicited_information = []  # list of elicited information objects
for record in csv_reader:
    if record[0] == 'source':  # skip header line in csv
        continue

    # instantiate new elicited info object
    information = elicited_info.ElicitedInformation(source=record[0], information=record[1])
    elicited_information.append(information)

csv_file.close()

# invoke the app GUI with initial dimensions
width = 900
height = 600
root = app.tk.Tk()
app = app.HexagonClusterApp(root, width, height)

# Add hexagons starting at (100, 100)
x = 100
y = 100
for information in elicited_information:
    app.add_hexagon(x, y, information.information)
    if x < width - 100:
        x += 100
        y = 100
    else:
        x = 100
        y += 100


# Bind export to HTML to a button click event to call the export_to_html method in app.py
export_button = app.setup_export_button()

root.mainloop()
