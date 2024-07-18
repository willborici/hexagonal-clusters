# main GUI app file

import tkinter as tk
from hexagon import HexagonDrawer


class HexagonClusterApp:
    def __init__(self, root, width, height):
        self.root = root
        self.root.title("Hexagonal Clusters")
        self.width = width
        self.height = height

        # Create a canvas to draw on
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height, bg='white')
        self.canvas.pack(padx=10, pady=10)

        # Initialize HexagonDrawer
        self.hexagon_drawer = HexagonDrawer(self.canvas)

    def add_hexagon(self, x, y, text):
        # Use HexagonDrawer to draw a hexagon
        self.hexagon_drawer.draw_hexagon(x, y, text)

    def export_to_html(self):
        width = self.width
        height = self.height
        self.hexagon_drawer.export_to_html(width, height)

    def setup_export_button(self):
        export_button = tk.Button(self.root, text="Export to HTML", command=self.export_to_html)
        export_button.pack()


