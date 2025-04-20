import tkinter
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage
from logic import *
from time import time
import sys
import os

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller"""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

SOFT_RED = "#CC4A4A"
SOFT_WHITE = "#F3F3F3"
SOFT_GREEN = "#52DF81"
SOFT_PURPLE = "#C854FE"

def text_to_type_show():
    #Refreshes the text to type area with a new text
    text_to_type.config(state='normal')
    text_to_type.replace("1.0", 'end', ' '.join(refresh_words()))
    text_to_type.config(state='disabled')
    text_to_type.tag_add("center", "1.0", "end")
    #Refreshes the timer to its default starting time
    try:
        timer_entry.config(state="normal")
        timer_entry.delete(0, "end")
        timer_entry.insert(0, "60")
        timer_entry.config(state="disabled")
    except Exception as e:
        # timer_entry is not defined
        print('The following error has occurred:', e)
    #Refreshes the user input area to default
    user_entry.config(state='normal')
    user_entry.delete(0, 'end')
    on_focus_out(event=None, entry=user_entry, text='Type here to start')
    reset_values()
    disable_button()
    # print(text_to_type.get(1.0, 'end'))

# ----------------------------------------------------------------
# Init -----------------------------------------------------------
window = Tk()
window.title("Typing Speedometer")
window.geometry("820x600")
window.configure(bg=SOFT_RED)

canvas = Canvas(
    window,
    bg=SOFT_RED,
    height=600,
    width=820,
    bd=0,
    highlightthickness=0,
    relief="ridge"
)
canvas.place(x=0, y=0)
# ----------------------------------------------------------------
# Timer----------------------------------------------------
# Used to keep track of the passed time
old_time = None

def timer_end():
    global old_time
    if old_time is not None and int(timer_entry.get()) <= 0:
        old_time = None
        user_entry.config(state='disabled')
        window.focus_set()
        enable_button()
        get_results(results)

def timer_update():
    global old_time
    if old_time is not None and time() - old_time > 1:
        old_time = time()
        time_left = int(timer_entry.get()) - 1
        timer_entry.config(state="normal")
        timer_entry.delete(0, 'end')
        timer_entry.insert(0, str(time_left))
        timer_entry.config(state="disabled")
    timer_end()
    window.after(10, timer_update)

def timer_start():
    global old_time
    if old_time is None:
        old_time = time()

timer_bg = PhotoImage(
    file=resource_path("./gui/entry_3.png"))
timer_entry_bg = canvas.create_image(
    708.5,
    370.75,
    image=timer_bg
)
timer_entry = Entry(
    font=("Arial BoldMT", 20 * -1),
    bd=0,
    bg=SOFT_WHITE,
    fg=SOFT_RED,
    disabledforeground=SOFT_RED,
    highlightthickness=0,
    justify='center'
)
timer_entry.place(
    x=681.0,
    y=353.5,
    width=55.0,
    height=32.5
)
#Sets the timer and stops the user to interact with it
timer_entry.insert(0, '60')
timer_entry.config(state="disabled")

timer_im = PhotoImage(
    file=resource_path("./gui/image_1.png"))
timer = canvas.create_image(
    652.0,
    370.0,
    image=timer_im
)
# ----------------------------------------------------------------
# Start button ------------------------------------------
#Disable
def disable_button():
    refresh_button.config(command=lambda: None, image=disable_btn_im)

#Enable
def enable_button():
    refresh_button.config(command=lambda :text_to_type_show(), image=active_btn_im)

disable_btn_im = PhotoImage(
    file=resource_path("./gui/button_2.png"))

active_btn_im = PhotoImage(
    file=resource_path("./gui/button_1.png"))

refresh_button = Button(
    image=active_btn_im,
    borderwidth=0,
    highlightthickness=0,
    activebackground=SOFT_RED,
    command=lambda :text_to_type_show(),
    relief="flat",
)
refresh_button.place(
    x=311.0,
    y=468.0,
    width=197.0,
    height=53.0
)

disable_button()

# ---------------------------------------------------------------------------------
# User entry area where they must type-----------------------------------------------
#Entries placeholders
def on_entry_click(event, entry, text):
    if entry.get() == text:
        entry.delete(0, 'end')
        entry.config(foreground="#000716")

def on_focus_out(event, entry, text):
    if entry.get() == "":
        entry.insert(0, text)
        entry.config(foreground="gray")

user_box_im = PhotoImage(
    file=resource_path("./gui/entry_2.png"))
user_entry_bg = canvas.create_image(
    409.5,
    370.0,
    image=user_box_im)

def validate(text):
    if len(text) == 1 and text not in ACCEPTED_CHARS and text != ' ' and text != '-':
        return False
    return True

user_entry = Entry(
    validate='key',
    validatecommand=(window.register(validate), "%S"),
    font=("Arial BoldMT", 20 * -1),
    bd=0,
    bg=SOFT_WHITE,
    fg="#000716",
    highlightthickness=0,
    justify='center',
)
user_entry.place(
    x=259.0,
    y=352.0,
    width=301.0,
    height=34.0
)
user_entry.insert('end', 'Type here to start')
user_entry.bind("<FocusIn>", lambda event: on_entry_click(event, user_entry, 'Type here to start'))
user_entry.bind("<FocusOut>", lambda event: on_focus_out(event, user_entry, 'Type here to start'))
user_entry.bind('<Key>', lambda event: [check_correct_char(event, entry=user_entry, widget=text_to_type), timer_start()])
# ----------------------------------------------------------------
# Main text area where to show to user what to type--------------------------------
text_to_type_im = PhotoImage(
    file=resource_path("./gui/entry_1.png"))
text_to_type_bg = canvas.create_image(
    409.5,
    171.5,
    image=text_to_type_im
)
text_to_type = Text(
    font=("Arial BoldMT", 36 * -1),
    bd=0,
    bg=SOFT_WHITE,
    fg=SOFT_RED,
    highlightthickness=0,
    wrap=tkinter.WORD
)
text_to_type.place(
    x=170.0,
    y=90.0,
    width=479.0,
    height=165.0
)

# Init tags for text color (red=basic, green=correct, purple=wrong)
text_to_type.tag_configure("center", justify='center')
text_to_type.tag_configure("basic", foreground=SOFT_RED)
text_to_type.tag_configure("correct", foreground=SOFT_GREEN)
text_to_type.tag_configure("wrong", foreground=SOFT_PURPLE)
text_to_type_show()
text_to_type.config(state="disabled")
# ----------------------------------------------------------------
# Results------------------------------------------------------
canvas.create_text(
    626.0,
    444.0,
    anchor="nw",
    text="Your Score:",
    fill=SOFT_WHITE,
    font=("Arial BoldMT", 16 * -1)
)

results_im = PhotoImage(
    file=resource_path("./gui/entry_4.png"))
results_bg = canvas.create_image(
    699.0,
    508.0,
    image=results_im
)
results = Text(
    font=("Arial BoldMT", 16 * -1),
    bd=0,
    bg=SOFT_RED,
    fg=SOFT_WHITE,
    highlightthickness=0,
)
results.place(
    x=626.0,
    y=470.0,
    width=146.0,
    height=74.0
)
results.insert("end",
               "CPM: 0\n"
               "WPM: 0")
results.config(state='disabled',)

window.resizable(False, False)

timer_update()
window.mainloop()