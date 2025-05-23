from random import shuffle
import os
import sys

word_list: list = []
typed_words: dict = {}
last_typed_char_index: int = -1
current_word_index: int = 0
# Used to check if the typed char should be checked or not
ACCEPTED_CHARS = list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.abspath(relative_path)

# Getting an array of 1k words from an api in blocks of 200 for each length (3 to 7 letters)
def get_words():
    with open(resource_path('words.txt'), 'r', encoding='utf-8') as file:
        return file.read().split(', ')

#Creates a new list and shows it
def refresh_words():
    global word_list
    word_list = get_words()
    shuffle(word_list)
    return word_list

# Scrolls down one line when at the 3rd line
def scroll_down(widget):
    char_index = f"1.{last_typed_char_index}"
    bbox = widget.bbox(char_index)
    if bbox:
        x, y, width, height = bbox
        if y >= 2 * height:
            widget.yview_scroll(1, 'units')

# Scroll up by one line when deleting the first char of a line, or more when deleting the space before that char
def scroll_up(widget):
    char_index = f"1.{last_typed_char_index}"
    bbox = widget.bbox(char_index)
    if bbox:
        x, y, width, height = bbox
        if y <= height:
            widget.yview_scroll(-1, 'units')

# Needs to be called AFTER index increase <----------- !!!!!!
def get_new_word_char_index():
    return len(' '.join(word_list[:current_word_index]))

def remove_extra_chars(entry):
    if entry.get().endswith(' '):
        entry.delete(0, 'end')


def reset_values():
    global typed_words
    global current_word_index
    global last_typed_char_index
    typed_words = {}
    current_word_index = 0
    last_typed_char_index = -1

#---------------------------------------------------------------------USER INPUT SECTION---------------------------------------------------------------------------------
#Well, it ended up being the central core of the code. It handles the user input, checking if it reflects the content in the text_to_type widget
#Changes color using tags giving a visual output to the user
def check_correct_char(event, entry, widget):
    global last_typed_char_index
    global current_word_index
    global typed_words
    char = event.char.lower()
    remove_extra_chars(entry=entry)

    if event.keysym == 'BackSpace' and last_typed_char_index > -1:

        #This here gets back the previous word that was typed in case you backspaced on a space. Also useful if user hit space multiple times by mistake or something
        if widget.get(1.0, 'end')[last_typed_char_index] == ' ':
            current_word_index -= 1
            entry.insert(0 ,typed_words[word_list[current_word_index]] + ' ') #Adding space at the end here so that the deleted chara will be the space and not the last char of the inserted word. It feels more natural
            typed_len = len(typed_words[word_list[current_word_index]])
            word_len = len(word_list[current_word_index])
            last_typed_char_index -= word_len - typed_len if typed_len < word_len else 1
            scroll_up(widget=widget)

        # Checking for length of inputted word in user entry, to then synchronize the text to type response in case the typed word is longer than required when deleting. Avoiding to "clear" chars that are no being removed
        # TLDR No weird behaviour when backspace
        if len(entry.get()) <= len(word_list[current_word_index]):
            [widget.tag_remove(tag, f"1.{last_typed_char_index}") for tag in widget.tag_names()]
            last_typed_char_index -= 1

    elif event.keysym == 'space':
        #When space is typed it will move the index to the beginning of the next word. Saving the user-typed word in a dictionary where the key is the correct word, picked from the words list
        typed_words[word_list[current_word_index]] = entry.get().replace(' ', '')
        current_word_index += 1
        last_typed_char_index = get_new_word_char_index()
        entry.delete(0, 'end')
        scroll_down(widget=widget)
        # *_, l = typed_words.items()
        # print(typed_words, l)

    #Way too many ands but I need them not to nest. Anyway checks if user didn't input weird chars (not totally sure if I need those ands anymore after I added the validation in gui, but whatever for now)
    elif char != '' and char in ACCEPTED_CHARS and len(entry.get()) < len(word_list[current_word_index]) and len(char) == 1:
        last_typed_char_index += 1
        if widget.get(f"1.{last_typed_char_index}") == char:
            widget.tag_add("correct", f"1.{last_typed_char_index}")
        else:
            widget.tag_add("wrong", f"1.{last_typed_char_index}")
        scroll_down(widget=widget)
    widget.tag_add("center", "1.0", "end")
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------LEADERBOARD/RESULTS SECTION--------------------------------------------------------------------------------

# Gets the amount of characters typed in one minute
def get_chars_per_minute():
    n = 0
    try:
        for k ,v in typed_words.items():
            for char in k:
                n+=1 if char == v[k.index(char)].lower() else 0
    except Exception as e:
        print("While getting the result, the following error has occurred: ", e)
    return n

#Gets and displays the final results
def get_results(widget):
    cpm = get_chars_per_minute()
    #Words per minute using the international standard average word length
    wpm = cpm // 5
    widget.config(state='normal')
    widget.replace('1.0', 'end',
                   f'CPM:  {cpm}\n'
                   f'WPM:  {wpm}')
    widget.config(state='disabled')
