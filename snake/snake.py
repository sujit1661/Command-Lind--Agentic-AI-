
import tkinter as tk
import random

class SnakeGame:
    def __init__(self, master):
        self.master = master
        master.title("Snake Game")

        self.width = 600
        self.height = 400
        self.canvas = tk.Canvas(master, width=self.width, height=self.height, bg="black")
        self.canvas.pack()

        self.snake = [(100, 100), (90, 100), (80, 100)]
        self.food = self.create_food()
        self.score = 0
        self.direction = "Right"

        self.score_label = tk.Label(master, text="Score: 0", font=("Arial", 12))
        self.score_label.pack()

        self.running = True

        master.bind("<KeyPress>", self.change_direction)

        self.update()

    def create_food(self):
        while True:
            x = random.randrange(0, self.width, 10)
            y = random.randrange(0, self.height, 10)
            if (x, y) not in self.snake:
                return (x, y)

    def move_snake(self):
        head_x, head_y = self.snake[0]
        if self.direction == "Right":
            new_head = (head_x + 10, head_y)
        elif self.direction == "Left":
            new_head = (head_x - 10, head_y)
        elif self.direction == "Up":
            new_head = (head_x, head_y - 10)
        elif self.direction == "Down":
            new_head = (head_x, head_y + 10)

        self.snake.insert(0, new_head)
        self.snake.pop()

    def check_collision(self):
        head_x, head_y = self.snake[0]
        if head_x < 0 or head_x >= self.width or head_y < 0 or head_y >= self.height:
            return True
        if self.snake[0] in self.snake[1:]:
            return True
        return False

    def check_food(self):
        if self.snake[0] == self.food:
            self.score += 1
            self.score_label.config(text="Score: " + str(self.score))
            self.food = self.create_food()
            head_x, head_y = self.snake[0]
            if self.direction == "Right":
                new_head = (head_x + 10, head_y)
            elif self.direction == "Left":
                new_head = (head_x - 10, head_y)
            elif self.direction == "Up":
                new_head = (head_x, head_y - 10)
            elif self.direction == "Down":
                new_head = (head_x, head_y + 10)
            self.snake.insert(0, new_head)

    def change_direction(self, event):
        if event.keysym == "Up" and self.direction != "Down":
            self.direction = "Up"
        elif event.keysym == "Down" and self.direction != "Up":
            self.direction = "Down"
        elif event.keysym == "Left" and self.direction != "Right":
            self.direction = "Left"
        elif event.keysym == "Right" and self.direction != "Left":
            self.direction = "Right"

    def draw(self):
        self.canvas.delete("all")
        for x, y in self.snake:
            self.canvas.create_rectangle(x, y, x + 10, y + 10, fill="green")
        self.canvas.create_rectangle(self.food[0], self.food[1], self.food[0] + 10, self.food[1] + 10, fill="red")

    def game_over(self):
        self.running = False
        self.canvas.delete("all")
        self.canvas.create_text(self.width/2, self.height/2, text="Game Over! Score: " + str(self.score), font=("Arial", 20), fill="white")

    def update(self):
        if self.running:
            self.move_snake()
            if self.check_collision():
                self.game_over()
                return
            self.check_food()
            self.draw()
            self.master.after(100, self.update) # Speed of the game

root = tk.Tk()
game = SnakeGame(root)
root.mainloop()
