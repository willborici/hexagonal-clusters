# class for drawing a hexagon, with mouse event binders for drag & drop
import math
from shapely.geometry import LineString


# Currently, this static function returns the distance between the midpoints of two sides, since
# the two docking sides are parallel, any point would do.
def distance_between_sides(side1_x1, side1_y1, side1_x2, side1_y2, side2_x1, side2_y1, side2_x2, side2_y2):
    # calculated the distance between the midpoint of side 1 and the midpoint of side 2
    midpoint_side1_x = (side1_x1 + side1_x2) / 2
    midpoint_side1_y = (side1_y1 + side1_y2) / 2
    midpoint_side2_x = (side2_x1 + side2_x2) / 2
    midpoint_side2_y = (side2_y1 + side2_y2) / 2

    distance = math.sqrt((midpoint_side2_x - midpoint_side1_x) ** 2 + (midpoint_side2_y - midpoint_side1_y) ** 2)

    return distance


# Static function to check if, during the dragging of a hexagon, its docking side
# is fully or partially coinciding with the nearest hexagon's corresponding docking side. If so, the
# dragged hexagon should be immediately moved to snap at midpoint, regardless of the
# self.snap_distance value. TODO figure out why the side1.intersects(side2) never returns True
def are_sides_coincident(side1_x1, side1_y1, side1_x2, side1_y2, side2_x1, side2_y1, side2_x2, side2_y2):
    # Calculate the slopes of the two sides
    slope1 = (side1_y2 - side1_y1) / (side1_x2 - side1_x1) if side1_x2 != side1_x1 else None
    slope2 = (side2_y2 - side2_y1) / (side2_x2 - side2_x1) if side2_x2 != side2_x1 else None

    # If the slopes are not equal, the sides are not parallel and do not coincide
    if slope1 != slope2:
        return False

    # define the two sides
    side1 = LineString([(side1_x1, side1_y1), (side1_x2, side1_y2)])
    side2 = LineString([(side2_x1, side2_y1), (side2_x2, side2_y2)])

    # Check if the two parallel sides intersect (i.e., partially coincide)
    if side1.intersects(side2):
        return True

    # Check if the two parallel sides are equal (i.e., fully coincide)
    if side1.equals(side2):
        return True

    # If no point on either side lies on the other, they don't coincide
    return False


class Hexagon:
    hexagon_id = 0  # Class-level identifier to track hexagon numbers and print them on GUI

    def __init__(self, canvas):
        self.canvas = canvas
        self.hexagons = []  # list to store hexagon properties and elicited info text
        self.selected_hexagon = None
        self.drag_data = {'x': 0, 'y': 0, 'item': None}
        self.snap_distance = 5  # to automatically snap a moving hexagon to a nearby one
        self.size = 55
        self.background_color = 'orange'
        self.outline_color = 'white'
        self.font = 'Consolas'
        self.font_size = 10
        self.truncation_mark = '[...]'
        self.cluster_ps_file = 'output/hexagonal_clusters.ps'  # Define cluster_ps_file for cluster output

    def draw(self, x, y, text):
        # Increment ID
        Hexagon.hexagon_id += 1

        # Define hexagon points into a list
        points = []
        for i in range(6):
            angle_deg = 60 * i + 30
            angle_rad = math.pi / 180 * angle_deg
            points.append(x + self.size * math.cos(angle_rad))
            points.append(y + self.size * math.sin(angle_rad))
        # draw hexagon with given points
        hexagon = self.canvas.create_polygon(points, outline=self.outline_color,
                                             fill=self.background_color, width=0.5)

        # Create a unique tag for the hexagon in order to bind it later to the mouse left-click
        # since polygons are not bound by default
        hexagon_tag = f"hexagon_{id(hexagon)}"

        # Add hexagon tag to the polygon object; then, use hexagon_tag in the
        # self.canvas.tag_bind statement in the if-block below for toggling long texts on/ off
        self.canvas.addtag_withtag(hexagon_tag, hexagon)

        # Display hexagon ID on top vertex, and save to hexagon_number to drag when hexagon moves
        hexagon_number = self.canvas.create_text(
            x, y - self.size + 7,
            text=str(Hexagon.hexagon_id),
            font=(self.font, self.font_size + 2),
            fill='navy'
        )

        # Define width for wrapping text:
        text_wrap_width = self.size * 0.85

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

        # Store hexagon data in a dictionary
        hexagon_data = {
            'hexagon': hexagon,
            'text_id': text_id,
            'hexagon_number': hexagon_number,
            'x': x,
            'y': y,
            'text': text
        }
        self.hexagons.append(hexagon_data)  # List of hexagon dictionaries

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
        hexagon_height = self.size * 0.85
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
            text_wrap_width = self.size * 0.85
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

        # TODO sometimes, by accident?, the text moves instead of the
        #      hexagon -- ensure this never happens with Tkinter
        # Move the hexagon and its associated text
        self.canvas.move(self.drag_data['item'], dx, dy)
        self.canvas.move(self.get_text_id(self.drag_data['item']), dx, dy)
        self.canvas.move(self.get_hexagon_number(self.drag_data['item']), dx, dy)

        # Update drag data
        self.drag_data['x'] = event.x
        self.drag_data['y'] = event.y

        # Check if any of the shift keys is pressed to activate auto-snapping
        if event.state & 0x1 or event.state & 0x2 or event.state & 0x2000:
            # see what's nearby to begin docking, given the hexagon being dragged
            self.check_for_docking()

    def check_for_docking(self):
        dragged_item = self.drag_data['item']  # ID of the hexagon being dragged
        dragged_item_coords = self.canvas.coords(dragged_item)  # coordinates of hexagon being moved

        # Iterate through all hexagons to find the nearest hexagon to dragged_item (hexagon being moved)
        already_snapped = False
        for hexagon_data in self.hexagons:
            hexagon = hexagon_data['hexagon']

            if hexagon == dragged_item:  # skip hexagon being dragged
                continue

            # if docking between multiple hexagons, snap only once, or else it shifts behind the
            # group of hexagons that are already docked
            if already_snapped:
                break

            hex_coords = self.canvas.coords(hexagon)

            # Iterate through each side of the current hexagon to find the closest two sides
            # between it and the hexagon being dragged.
            for dragged_side_index in range(6):
                # Coordinates of the side of the hexagon being dragged
                dragged_side_x_start = dragged_item_coords[2 * dragged_side_index]
                dragged_side_y_start = dragged_item_coords[2 * dragged_side_index + 1]
                dragged_side_x_end = dragged_item_coords[2 * ((dragged_side_index + 1) % 6)]
                dragged_side_y_end = dragged_item_coords[2 * ((dragged_side_index + 1) % 6) + 1]

                for hex_side_index in range(6):
                    # Coordinates of the sides of the current hexagon
                    hex_side_x_start = hex_coords[2 * hex_side_index]
                    hex_side_y_start = hex_coords[2 * hex_side_index + 1]
                    hex_side_x_end = hex_coords[2 * ((hex_side_index + 1) % 6)]
                    hex_side_y_end = hex_coords[2 * ((hex_side_index + 1) % 6) + 1]

                    # Calculate distances between the midpoints of the sides of dragged hexagon
                    # and current hexagon (because the sides are parallel, any coord would do)
                    current_distance_between_sides = distance_between_sides(
                        dragged_side_x_start, dragged_side_y_start, dragged_side_x_end, dragged_side_y_end,
                        hex_side_x_start, hex_side_y_start, hex_side_x_end, hex_side_y_end
                    )

                    # Check if the two sides partially coincide, so that the snapping happens
                    # regardless of the snapping distance
                    sides_coincide = are_sides_coincident(dragged_side_x_start, dragged_side_y_start,
                                                          dragged_side_x_end, dragged_side_y_end,
                                                          hex_side_x_start, hex_side_y_start, hex_side_x_end,
                                                          hex_side_y_end)

                    # Dock as you go if any of the current hexagon's sides to any of the
                    # dragged hexagon's sides is less than the snapping distance, or if the two sides
                    # are already coincident, in which case just dock them at midpoint
                    if current_distance_between_sides < self.snap_distance or sides_coincide:
                        # Closest hexagon's closest side's coordinates:
                        docking_midpoint_x = (hex_side_x_start + hex_side_x_end) / 2
                        docking_midpoint_y = (hex_side_y_start + hex_side_y_end) / 2

                        # Calculate the midpoint of the dragged hexagon's side
                        dragged_midpoint_x = (dragged_side_x_start + dragged_side_x_end) / 2
                        dragged_midpoint_y = (dragged_side_y_start + dragged_side_y_end) / 2

                        # Calculate the delta x and delta y to move the dragged hexagon to align
                        # with the nearest hexagon's side based on the docking position and the side indices
                        dx = docking_midpoint_x - dragged_midpoint_x
                        dy = docking_midpoint_y - dragged_midpoint_y

                        # Move the dragged hexagon and its associated text and number
                        self.canvas.move(dragged_item, dx, dy)
                        self.canvas.move(self.get_text_id(dragged_item), dx, dy)
                        self.canvas.move(self.get_hexagon_number(dragged_item), dx, dy)

                        already_snapped = True

    def get_text_id(self, hexagon_id):
        # Find text_id associated with hexagon_id, so we drag the
        # elicited information (stored in text) along with corresponding hexagon
        for hexagon in self.hexagons:
            if hexagon['hexagon'] == hexagon_id:
                return hexagon['text_id']
        return None

    def get_hexagon_number(self, hexagon_id):
        # Find the hexagon_number associated with hexagon_id, so we drag the
        # elicited information (stored in text) along with corresponding hexagon
        for hexagon in self.hexagons:
            if hexagon['hexagon'] == hexagon_id:
                return hexagon['hexagon_number']
        return None

    # TODO figure out why the correctly exported PS is not rendered by the HTML JS
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
