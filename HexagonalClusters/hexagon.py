# class for drawing a hexagon, with mouse event binders for drag & drop

class HexagonDrawer:
    hexagon_id = 0  # Class-level identifier to track hexagon numbers and print them on GUI

    def __init__(self, canvas):
        self.canvas = canvas
        self.hexagons = []  # list to store hexagon properties and elicited info text
        self.selected_hexagon = None
        self.drag_data = {'x': 0, 'y': 0, 'item': None}
        self.hexagon_size = 50
        self.font = 'Consolas'
        self.font_size = 10
        self.truncation_mark = '[...]'
        self.cluster_ps_file = 'output/hexagonal_clusters.ps'  # Define cluster_ps_file for cluster output

    def draw_hexagon(self, x, y, text):
        # Increment ID
        HexagonDrawer.hexagon_id += 1

        # Draw hexagon polygon
        hexagon = self.canvas.create_polygon(
            x, y - self.hexagon_size,
               x + self.hexagon_size * 0.866, y - self.hexagon_size / 2,
               x + self.hexagon_size * 0.866, y + self.hexagon_size / 2,
            x, y + self.hexagon_size,
               x - self.hexagon_size * 0.866, y + self.hexagon_size / 2,
               x - self.hexagon_size * 0.866, y - self.hexagon_size / 2,
            outline='navy', fill='orange', width=0.5
        )

        # Create a unique tag for the hexagon in order to bind it later to the mouse left-click
        # since polygons are not bound by default
        hexagon_tag = f"hexagon_{id(hexagon)}"

        # Add hexagon tag to the polygon object; then, use hexagon_tag in the
        # self.canvas.tag_bind statement in the if-block below for toggling long texts on/ off
        self.canvas.addtag_withtag(hexagon_tag, hexagon)

        # Display hexagon ID on top vertex, and save to hexagon_number to drag when hexagon moves
        hexagon_number = self.canvas.create_text(
            x, y - self.hexagon_size + 7,
            text=str(HexagonDrawer.hexagon_id),
            font=(self.font, self.font_size + 2),
            fill='navy'
        )

        # Define width for wrapping text:
        text_wrap_width = self.hexagon_size * 0.85

        # Check if text exceeds 85% of the hexagon width
        if self.text_exceeds_width(text, text_wrap_width):
            text_id = self.canvas.create_text(
                x, y,
                text=self.wrap_text(text, text_wrap_width),
                font=(self.font, self.font_size), fill='black'
            )

            # Store full text in a tag singleton to retrieve later when user drags hexagon
            self.canvas.itemconfig(text_id, tags=(text,))

            # Bind click event to hexagon to toggle full text visibility on or off
            self.canvas.tag_bind(hexagon_tag, '<Button-1>',
                                 lambda event, info_id=text_id, full_text=text: self.toggle_full_text(event, info_id,
                                                                                                      full_text))
        else:
            # Draw text directly inside hexagon as is
            text_id = self.canvas.create_text(x, y, text=text, font=(self.font, self.font_size), fill='black')

        # Store hexagon data tuple with indices: [0, 1, 2, 3, 4, 5, ...]
        self.hexagons.append((hexagon, text_id, hexagon_number, x, y, text))

        # Bind drag events
        self.bind_drag(hexagon)

    def text_exceeds_width(self, text, width):
        # Check if the text exceeds the specified width
        return self.canvas.bbox(self.canvas.create_text(0, 0, text=text, font=(self.font, self.font_size)))[2] > width

    # Given elicited information text, split it word by word such that the split words form
    # lines that fit into the hexagon's width. If the total number of lines exceed the
    # hexagon's height, use the truncate_text method separately inside the draw_hexagon method
    def wrap_text(self, text, width):
        # Split text into lines, such that each split line fits within the hexagon width,
        # and if the split lines exceed the hexagon's height, truncate them:
        # Define hexagon height, given hexagon_size:
        hexagon_height = self.hexagon_size * 0.85
        current_text_height = 0  # record current text height for each wrapped line

        lines = []
        words = text.split()
        while words:
            line = words.pop(0)

            while words and not self.text_exceeds_width(' '.join([line, words[0]]), width):
                line = ' '.join([line, words.pop(0)])
            lines.append(line + '\n')  # break lines to fit into hexagon

            current_text_height += self.font_size  # each line contributes its font size to the height
            # check if current text height exceeds the hexagon height:
            if current_text_height > hexagon_height:
                # Truncate the last line and break
                lines[-1] = self.truncation_mark.strip('\n')  # replace previous line with truncation mark
                break

        return ''.join(lines)  # concatenate list of lines into a string

    def truncate_text(self, text, width):
        # Truncate text to fit within the specified width
        while self.text_exceeds_width(text, width):
            text = text[:-1]  # keep truncating until truncated text is within width
        return text + self.truncation_mark

    def toggle_full_text(self, event, text_id, full_text):
        current_text = self.canvas.itemcget(text_id, 'text')

        if current_text.endswith(self.truncation_mark):
            # Show full text
            self.canvas.itemconfig(text_id, text=full_text)
        else:
            # Show truncated text
            text_wrap_width = self.hexagon_size * 0.85
            self.canvas.itemconfig(text_id, text=self.wrap_text(full_text, text_wrap_width))

    def bind_drag(self, hexagon):
        self.canvas.tag_bind(hexagon, '<ButtonPress-1>', self.on_drag_start)
        self.canvas.tag_bind(hexagon, '<ButtonRelease-1>', self.on_drag_end)
        self.canvas.tag_bind(hexagon, '<B1-Motion>', self.on_drag_motion)

    def on_drag_start(self, event):
        # Determine which hexagon was clicked
        self.selected_hexagon = event.widget.find_closest(event.x, event.y)[0]

        # Store drag data, so that we move any text and hexagon number associated with this hexagon
        self.drag_data['item'] = self.selected_hexagon
        self.drag_data['x'] = event.x
        self.drag_data['y'] = event.y

    def on_drag_end(self, event):
        # Reset selected hexagon and data
        self.selected_hexagon = None
        self.drag_data['item'] = None
        self.drag_data['x'] = 0
        self.drag_data['y'] = 0

    def on_drag_motion(self, event):
        # Calculate movement distance
        dx = event.x - self.drag_data['x']
        dy = event.y - self.drag_data['y']

        # Move the hexagon and its associated text
        self.canvas.move(self.drag_data['item'], dx, dy)
        self.canvas.move(self.get_text_id(self.drag_data['item']), dx, dy)
        self.canvas.move(self.get_hexagon_number(self.drag_data['item']), dx, dy)

        # Update drag data
        self.drag_data['x'] = event.x
        self.drag_data['y'] = event.y

    def get_text_id(self, hexagon_id):
        # Find text_id associated with hexagon_id, so we drag the
        # elicited information (stored in text) along with corresponding hexagon
        for hexagon in self.hexagons:
            if hexagon[0] == hexagon_id:
                return hexagon[1]  # text is stored in the second hexagon tuple position in draw_hexagon()
        return None

    def get_hexagon_number(self, hexagon_id):
        # Find the hexagon_number associated with hexagon_id, so we drag the
        # elicited information (stored in text) along with corresponding hexagon
        for hexagon in self.hexagons:
            if hexagon[0] == hexagon_id:
                return hexagon[2]  # hexagon_number is stored in the third hexagon tuple position in draw_hexagon()
        return None

    def export_to_html(self, width, height):
        # Create the PostScript file with canvas data
        self.canvas.postscript(file=self.cluster_ps_file, colormode='color')

        # Create HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Hexagon Layout</title>
            <script type="text/javascript">
                function drawHexagons() {{
                    var canvas = document.getElementById('hexagonCanvas');
                    var ctx = canvas.getContext('2d');

                    var img = new Image();
                    img.onload = function() {{
                        ctx.drawImage(img, 0, 0);
                    }};
                    img.src = '{self.cluster_ps_file}';
                }}
            </script>
        </head>
        <body onload="drawHexagons()">
            <canvas id="hexagonCanvas" width="{width}" height="{height}" style="border:1px solid #eee;">
                Your browser does not support the HTML5 canvas tag.
            </canvas>
        </body>
        </html>
        """

        # Write HTML content to a file in the current directory
        with open('output/hexagon_layout.html', 'w') as html_file:
            html_file.write(html_content)
        html_file.close()
