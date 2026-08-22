import time
import tkinter as tk
from tkinter import StringVar, ttk
from PIL import Image, ImageTk
import pyttsx3
import threading

class BaseApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.lock=threading.Lock()
        self.Setup_Style()
    def setup_background(self):
            """Initialize the background slideshow"""
            self.bg_frame = tk.Frame(self)
            self.bg_frame.place(x=0, y=0, relwidth=1, relheight=1)
            
            self.bg_canvas = tk.Canvas(self.bg_frame)
            self.bg_canvas.pack(fill="both", expand=True)
            self.image_paths = [
                r"F:\QuizApp\my_images\1.PNG",
                r"F:\QuizApp\my_images\2.PNG",
                r"F:\QuizApp\my_images\3.PNG",
                r"F:\QuizApp\my_images\4.PNG",
                r"F:\QuizApp\my_images\5.PNG",
                r"F:\QuizApp\my_images\6.PNG",
                r"F:\QuizApp\my_images\7.PNG",
                r"F:\QuizApp\my_images\8.PNG"
            ]
            
            # Load images
            self.original_images = []
            for path in self.image_paths:
                try:
                    img = Image.open(path)
                    self.original_images.append(img)
                except Exception as e:
                    print(f"Error loading image {path}: {e}")
            
            if not self.original_images:
                self.bg_canvas.config(bg='purple4')
                return
                
            # Slideshow variables
            self.current_bg_index = 0
            self.bg_photo_images = []
            
            # Start slideshow
            self.update_background()

    def update_background(self):
            """Update the background image"""
            if not self.bg_canvas.winfo_exists():
                return
                
            try:
                # Get current dimensions
                width = self.bg_canvas.winfo_width()
                height = self.bg_canvas.winfo_height()
                
                if width > 1 and height > 1:  # Valid dimensions
                    # Resize and display image
                    img = self.original_images[self.current_bg_index]
                    resized = img.resize((width, height), Image.Resampling.LANCZOS)
                    photo_img = ImageTk.PhotoImage(resized)
                    
                    # Keep reference and update
                    self.bg_photo_images.append(photo_img)
                    if len(self.bg_photo_images) > 2:  # Keep only recent images
                        self.bg_photo_images.pop(0)
                    
                    self.bg_canvas.delete("bg")
                    self.bg_canvas.create_image(0, 0, image=photo_img, anchor="nw", tags="bg")
                
                # Cycle to next image
                self.current_bg_index = (self.current_bg_index + 1) % len(self.original_images)
                self.after(3000, self.update_background)
                
            except Exception as e:
                print(f"Background error: {e}")

    def Setup_Style(self):
            self.style = ttk.Style()
            self.style.configure('TButton', font=('calibri', 16,"italic",'underline','bold'), padding=10,foreground = 'red',background='floral white')
            self.style.configure('Title.TLabel', font=('Arial', 20, 'bold',"italic"), foreground='black',background='floral white')
            self.style.configure('Text.TLabel', font=('calibri', 14, 'bold'), foreground='black',background='floral white')
            self.style.configure('TexT.TLabel', font=('calibri', 14, 'bold'), foreground='red',background='floral white')
            self.style.configure('Question.TLabel', font=('Arial', 18), foreground='black',background='floral white')
            self.style.configure('Option.TRadiobutton', font=('Arial', 14), foreground='black',background='floral white')
            self.style.configure('Timer.TLabel', font=('Arial', 14, 'bold'), foreground='red', background='floral white')
            self.style.configure("Green.TLabel", font=('Segoe UI', 14), foreground="#043488", background='floral white')
            self.style.configure('Question.TButton', font=('Arial', 12,'underline','bold'), foreground='Black', background="green")
    def clear_screen(self):
        """Clear screen but keep background and robot"""
        for widget in self.winfo_children():
            if widget != self.bg_frame:
                widget.destroy()

    
    def create_screen(self):
        frame = tk.Frame(self, bg='floral white')
        frame.pack(expand=True, fill="both", padx=160, pady=60)
        return frame
    
    def setup_robot(self, help_callback, parent_frame):
        self.robot_frames = []
        image_paths = [
            r"F:\QuizApp\my_images\robo.png",
            r"F:\QuizApp\my_images\robo 2.PNG",
            r"F:\QuizApp\my_images\robo 3.PNG",
            r"F:\QuizApp\my_images\robo 4.PNG",
            r"F:\QuizApp\my_images\images (2).jpg",
            r"F:\QuizApp\my_images\images.jpg"
        ]

        for path in image_paths:
            img = Image.open(path).resize((80, 80))
            self.robot_frames.append(ImageTk.PhotoImage(img))

        self.current_robot_frame = 0

        self.robot_label = tk.Label(parent_frame, image=self.robot_frames[0], bg="white", cursor="hand2")
        self.robot_label.image = self.robot_frames[0]
        self.robot_label.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-10)

        self.hover_label = tk.Label(parent_frame, text="Hi ! Buddy, I am Robo.\nMay I Help You?", bg="floral white", font=("Arial", 14, "bold"))
        self.robot_label.bind("<Enter>", lambda e: self.hover_label.place(relx=1.0, rely=1.0, anchor='se', x=-100, y=-100))
        self.robot_label.bind("<Leave>", lambda e: self.hover_label.place_forget())
        self.robot_label.bind("<Button-1>", lambda e: help_callback())

        self.animate_robot()

    def animate_robot(self):
        if not hasattr(self, 'robot_label') or not hasattr(self, 'robot_frames'):
            return
        if not self.robot_label.winfo_exists():
            return
        self.robot_label.config(image=self.robot_frames[self.current_robot_frame])
        self.robot_label.image = self.robot_frames[self.current_robot_frame]
        self.current_robot_frame = (self.current_robot_frame + 1) % len(self.robot_frames)
        self.after(3000, self.animate_robot)
        
    def speak(self, audio):
        def run_speech():
            with self.lock: 
                engine = pyttsx3.init("sapi5")
                voices = engine.getProperty("voices")
                engine.setProperty("voice", voices[1].id)
                rate = engine.getProperty("rate")
                engine.setProperty("rate", rate - 75)
                volume = engine.getProperty("volume")
                engine.setProperty("volume", min(volume * 2.0, 1.0))      
                engine.say(audio)
                engine.runAndWait()
        threading.Thread(target=run_speech, daemon=True).start()
            
            
