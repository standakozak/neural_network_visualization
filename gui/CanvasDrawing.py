import tkinter as tk
import numpy as np
from PIL import Image, ImageDraw, ImageTk


class CanvasDrawing(tk.Frame):
    WIDTH_DRAW_CANVAS = 560
    HEIGHT_DRAW_CANVAS = 560

    WIDTH_SHOW_CANVAS = 280
    HEIGHT_SHOW_CANVAS = 280

    ARRAY_COLS = 28
    ARRAY_ROWS = 28

    WIDTH_FACTOR = WIDTH_DRAW_CANVAS // ARRAY_COLS
    HEIGHT_FACTOR = HEIGHT_DRAW_CANVAS // ARRAY_ROWS

    def __init__(self, container, controller):
        tk.Frame.__init__(self, container)
        self.root = container
        self.controller = controller

        self.drawing_as_input = np.zeros((self.ARRAY_ROWS, self.ARRAY_COLS))

        self.canvas_draw = tk.Canvas(self, bg="white", height=self.HEIGHT_DRAW_CANVAS, width=self.WIDTH_DRAW_CANVAS)
        self.canvas_draw.grid(column="0", row="0")
        self.canvas_show = tk.Canvas(self, bg="white", height=self.HEIGHT_SHOW_CANVAS, width=self.WIDTH_SHOW_CANVAS)
        self.canvas_show.grid(column="1", row="0")

        self.pil_image = Image.new("P", (self.WIDTH_DRAW_CANVAS, self.HEIGHT_DRAW_CANVAS), (255, 255, 255))
        self.pil_draw = ImageDraw.Draw(self.pil_image)

        self.canvas_draw.bind("<Button-1>", self.get_x_and_y)
        self.canvas_draw.bind("<B1-Motion>", self.draw)
        self.canvas_draw.bind("<Button-3>", self.get_x_and_y)
        self.canvas_draw.bind("<B3-Motion>", self.clear)

        tk.Button(self, text='Main Screen', bg='#FFFFFF', font=('arial', 15, 'normal'), command=lambda: self.controller.show_frame("MainScreen")).grid(row=1, column=1)
        tk.Button(self, text='Clear', bg='#FFFFFF', font=('arial', 15, 'normal'), command=self.clear_canvas).grid(row=1, column=0)

        self.output_label = tk.Label(self, text="", font=('arial', 15, 'normal'))
        self.output_label.grid(row=0, column=2, rowspan=2)

    def create_resized_image(self):
        original_image = self.pil_image
        original_array = np.asarray(original_image)
        resized = []
        for row in range(0, self.HEIGHT_DRAW_CANVAS, self.HEIGHT_FACTOR):
            resized_row = []
            for col in range(0, self.WIDTH_DRAW_CANVAS, self.WIDTH_FACTOR):
                resized_row.append((original_array[row:row+self.HEIGHT_FACTOR, col:col+self.WIDTH_FACTOR]).mean())
            resized.append(resized_row)
        self.drawing_as_input = np.asarray(resized)
        drawing_array = 255 * (1 - self.drawing_as_input)

        resized_image = Image.fromarray(drawing_array.astype(np.uint8))
        self.resized_photo_image = ImageTk.PhotoImage(resized_image.resize(size=(self.HEIGHT_SHOW_CANVAS, self.WIDTH_SHOW_CANVAS)))

    def get_x_and_y(self, event):
        self.lasx, self.lasy = event.x, event.y

    def draw_on_both_canvases(self, event, width, color="black"):
        color_rgb = (0, 0, 0)
        if color == "white":
            color_rgb = (255, 255, 255)
        self.canvas_draw.create_line((self.lasx, self.lasy, event.x, event.y), 
                        fill=color, 
                        width=width)
        self.pil_draw.line((self.lasx, self.lasy, event.x, event.y), color_rgb, width=width)
        self.create_resized_image()

        self.canvas_show.create_image(self.HEIGHT_SHOW_CANVAS//2, self.WIDTH_SHOW_CANVAS//2, image=self.resized_photo_image)
        self.controller.test_drawn_image(self.drawing_as_input)

        self.lasx, self.lasy = event.x, event.y

    def draw(self, event):
        self.draw_on_both_canvases(event=event, width=8, color="black")

    def clear(self, event):
        self.draw_on_both_canvases(event=event, width=16, color="white")
    
    def clear_frame(self, event):
        for widget in self.winfo_children():
            widget.destroy()

    def clear_canvas(self):
        self.canvas_draw.delete("all")
        self.pil_draw.rectangle((0, 0, self.WIDTH_DRAW_CANVAS, self.HEIGHT_DRAW_CANVAS), fill=(255, 255, 255))
        self.create_resized_image()
        self.controller.test_drawn_image(self.drawing_as_input)

    def display_probabilities(self, probabilities):
        text = ""
        for answer, probability in probabilities:
            text += f"{str(answer)}: {round(float(probability), 2)} %\n"
        self.output_label["text"] = text

    def update_elements(self):
        pass


if __name__ == "__main__":
    from main import NeuralNetworksGUI
    main_app = NeuralNetworksGUI()
    #main_app.show_frame("CanvasDrawing")
    main_app.mainloop()