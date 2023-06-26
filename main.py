from tkinter import *
import customtkinter as ctk
from tkinter import messagebox
import pandas
import random
import sqlite3
import requests
import pygame


connection = sqlite3.connect("vocabulary.db")
cursor = connection.cursor()
url = 'http://ip_address:5000/translate'

language_selected = ""
save = 0
level = 0
new_game = False
save_to_load = ""
to_learn = []
current_card = ""
BACKGROUND_COLOR = "#FCE3B6"

window = Tk()
window.title("Word Up")
window.config(bg=BACKGROUND_COLOR)
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
side = int(min(screen_height*0.7, screen_width*0.7))
window.minsize(width=side, height=side)
window.resizable(False, False)
window.grid_rowconfigure(0, weight=1)
window.grid_columnconfigure(0, weight=1)


# ----------------------------- MAIN MENU -------------------------------------------------------------------
def show_frame(page):
    page.tkraise()


def new_track():
    global new_game
    new_game = True
    show_frame(language_page)
    select_save_label.config(text="Select a save file to start:")


def load_track():
    show_frame(language_page)
    select_save_label.config(text="Select a save file to load:")


def continue_track():
    global save_to_load, to_learn, level
    with open("data/recent_save.txt", 'r') as file_1:
        save_to_load = file_1.read()
    try:
        cursor.execute(f"select * from {save_to_load}")
    except sqlite3.OperationalError:
        show_frame(level_complete)
    else:
        word_list = cursor.fetchall()
        to_learn = [tup[0] for tup in word_list]
        cursor.execute(f"select * from saves_list where save_name = '{save_to_load}'")
        records = cursor.fetchall()
        level = records[0][1]
        total_word_count = level_to_word[level]
        words_learnt = total_word_count - len(to_learn)
        stats_label.config(text=f"Level: {level}\nWords learnt: {words_learnt}/{total_word_count}")
        show_frame(game_page)
        next_card()


main_menu = Frame(window)
main_menu.grid(row=0, column=0, sticky="nsew")

main_menu.grid_rowconfigure(0, weight=0)
main_menu.grid_rowconfigure(1, weight=1)
main_menu.grid_rowconfigure(2, weight=1)
main_menu.grid_rowconfigure(3, weight=1)
main_menu.grid_columnconfigure(0, weight=1)

title_logo = PhotoImage(file="images/title_logo.png")
title_label = Label(main_menu, image=title_logo)
title_label.grid(row=0, column=0)

continue_img = PhotoImage(file='images/continue_button.png')
continue_button = Button(main_menu, image=continue_img, command=continue_track, borderwidth=0)
with open("data/recent_save.txt") as file:
    if file.readline() != "empty":
        continue_button.grid(row=1, column=0)

new_img = PhotoImage(file='images/new_button.png')
new_button = Button(main_menu, image=new_img, command=new_track, borderwidth=0)
new_button.grid(row=2, column=0)

load_img = PhotoImage(file='images/load_button.png')
load_button = Button(main_menu, image=load_img, command=load_track, borderwidth=0)
load_button.grid(row=3, column=0)


# ----------------------------- LANGUAGE SELECT PAGE ------------------------------------------------------------------
def load_pages(language):
    global language_selected
    show_frame(saves_page)
    saves_page_title.config(text=language)
    levels_page_title.config(text=language)
    language_selected = language.lower()


language_page = Frame(window)
language_page.grid(row=0, column=0, sticky="nsew")
language_page.grid_rowconfigure(0, weight=1)
language_page.grid_rowconfigure(1, weight=1)
language_page.grid_rowconfigure(2, weight=1)
language_page.grid_rowconfigure(3, weight=1)
language_page.grid_columnconfigure(0, weight=1)

select_lang_label = Label(language_page, text="Select language:")
select_lang_label.grid(row=0, column=0)

# fr_button_img = PhotoImage(file="images/french_button.png")
# french_button = Button(language_page, image=fr_button_img, command=lambda: load_pages("French"), borderwidth=0)
# sp_button_img = PhotoImage(file="images/spanish_button.png")
# spanish_button = Button(language_page, image=sp_button_img, command=lambda: load_pages("Spanish"), borderwidth=0)
ko_button_img = PhotoImage(file="images/korean_button.png")
korean_button = Button(language_page, image=ko_button_img, command=lambda: load_pages("Korean"), borderwidth=0)

# french_button.grid(row=1, column=0)
# spanish_button.grid(row=2, column=0)
korean_button.grid(row=1, column=0)


# ----------------------------- SAVE SELECT PAGE ----------------------------------------------------------------
def delete_save(save_to_delete):
    cursor.execute(f"drop table {save_to_delete}")
    cursor.execute(f"delete from saves_list where save_name = '{save_to_delete}'")


def set_save(n):
    global save, save_to_load
    save = n
    save_to_load = f"{language_selected}_save_{save}"
    try:
        cursor.execute(f"select * from {save_to_load}")
    except sqlite3.OperationalError:
        with open("data/recent_save.txt", 'w') as file_1:
            file_1.write(f"{save_to_load}")
        cursor.execute(f"insert into saves_list values('{save_to_load}', 0)")
        return True
    else:
        if cursor.fetchall() and new_game:
            to_delete = messagebox.askyesno(title="Oops", message=f"Save {save} is already occupied!!!"
                                                                  f"\n Do you want to delete it?")
            if to_delete:
                delete_save(save_to_load)
                with open("data/recent_save.txt", 'w') as file_1:
                    file_1.write(f"{save_to_load}")
                cursor.execute(f"insert into saves_list values('{save_to_load}', 0)")
                return True
            else:
                return False
        else:
            with open("data/recent_save.txt", 'w') as file_1:
                file_1.write(f"{save_to_load}")
            cursor.execute(f"insert into saves_list values('{save_to_load}', 0)")
            return True


def load_levels_n(n):
    if set_save(n):
        show_frame(levels_page)


def load_save_n(n):
    global save, save_to_load, to_learn, level
    save = n
    save_to_load = f"{language_selected}_save_{save}"
    try:
        cursor.execute(f"select * from {save_to_load}")
    except sqlite3.OperationalError:
        cursor.execute(f"select * from saves_list where save_name = '{save_to_load}'")
        if cursor.fetchall():
            show_frame(level_complete)
        else:
            messagebox.showinfo(title="Empty Save", message=f"Save {n} is empty.\nChoose another save file.")
    else:
        with open("data/recent_save.txt", 'w') as file_1:
            file_1.write(f"{save_to_load}")
        word_list = cursor.fetchall()
        to_learn = [tup[0] for tup in word_list]
        cursor.execute(f"select * from saves_list where save_name = '{save_to_load}'")
        records = cursor.fetchall()
        level = records[0][1]
        total_word_count = level_to_word[level]
        words_learnt = total_word_count - len(to_learn)
        stats_label.config(text=f"Level: {level}\nWords learnt: {words_learnt}/{total_word_count}")
        show_frame(game_page)
        next_card()


saves_page = Frame(window)
saves_page.grid(row=0, column=0, sticky="nsew")

saves_page.grid_rowconfigure(0, weight=0)
saves_page.grid_rowconfigure(1, weight=1)
saves_page.grid_rowconfigure(2, weight=1)
saves_page.grid_rowconfigure(3, weight=1)
saves_page.grid_rowconfigure(4, weight=1)
saves_page.grid_columnconfigure(0, weight=1)

saves_page_title = Label(saves_page, text="", font=("", 36))
saves_page_title.grid(row=0, column=0, pady=20)

select_save_label = Label(saves_page, text="")
select_save_label.grid(row=1, column=0)

save1_button = Button(saves_page, text="Save 1", command=lambda: load_levels_n(1) if new_game else load_save_n(1))
save1_button.grid(row=2, column=0)

save2_button = Button(saves_page, text="Save 2", command=lambda: load_levels_n(2) if new_game else load_save_n(2))
save2_button.grid(row=3, column=0)

save3_button = Button(saves_page, text="Save 3", command=lambda: load_levels_n(3) if new_game else load_save_n(3))
save3_button.grid(row=4, column=0)


# ----------------------------- LEVEL SELECT PAGE ---------------------------------------------------------------
def load_level_n(n):
    global level, to_learn
    level = n
    cursor.execute(f"update saves_list set level = {n} where save_name = '{save_to_load}'")
    cursor.execute(f"select * from korean_full")
    records = cursor.fetchall()
    word_count = level_to_word[n]
    to_learn = [tup[0] for tup in records][0:word_count]
    show_frame(game_page)
    word_count = level_to_word[level]
    stats_label.config(text=f"Level: {level}\nWords learnt: 0/{word_count}")
    next_card()


levels_page = Frame(window)
levels_page.grid(row=0, column=0, sticky="nsew")

levels_page.grid_rowconfigure(0, weight=0)
levels_page.grid_rowconfigure(1, weight=1)
levels_page.grid_rowconfigure(2, weight=1)
levels_page.grid_columnconfigure(0, weight=1)

levels_page_title = Label(levels_page, text="", font=("", 36))
levels_page_title.grid(row=0, column=0, pady=20)

level_select_label = Label(levels_page, text="Select a level to start learning:")
level_select_label.grid(row=1, column=0)

levels_container = Frame(levels_page)
levels_container.grid(row=2, column=0)

level_to_word = {
    1: 15,
    2: 30,
    3: 60,
    4: 120,
    5: 250,
    6: 500,
    7: 1000
}

row_n = 0
column_n = 0
for i in range(7):
    button_i = Button(
        levels_container,
        text=f"{i + 1}\n{level_to_word[i+1]} words",
        width=8, height=2,
        command=lambda j=i: load_level_n(j+1)
    )
    button_i.grid(row=row_n, column=column_n, padx=10, pady=10)
    column_n = (column_n + 1) % 4
    if column_n == 0:
        row_n += 1

# ----------------------------- LEVEL COMPLETE PAGE -------------------------------------------------------------
def home():
    show_frame(main_menu)


def next_level():
    global level, save_to_load, to_learn
    cursor.execute(f"select * from saves_list where save_name = '{save_to_load}'")
    records = cursor.fetchall()
    current_level = records[0][1]
    level = current_level + 1
    if level == 8:
        level = 1
        # Language Complete!
    cursor.execute(f"update saves_list set level = {level} where save_name = '{save_to_load}'")
    total_word_count = level_to_word[level]
    cursor.execute(f"select * from korean_full")
    records = cursor.fetchall()
    to_learn = [tup[0] for tup in records][0:total_word_count]
    stats_label.config(text=f"Level: {level}\nWords learnt: 0/{total_word_count}")
    show_frame(game_page)
    next_card()


def replay():
    global to_learn, level
    cursor.execute(f"select * from saves_list where save_name = '{save_to_load}'")
    records = cursor.fetchall()
    level = records[0][1]
    total_word_count = level_to_word[level]
    cursor.execute(f"select * from korean_full")
    records = cursor.fetchall()
    to_learn = [tup[0] for tup in records][0:total_word_count]
    data_to_learn = pandas.DataFrame(to_learn)
    try:
        data_to_learn.to_sql(name=f"{save_to_load}", con=connection, schema="Korean nvarchar(30)", if_exists="replace", index=False)
    except sqlite3.OperationalError:
        show_frame(level_complete)
    else:
        stats_label.config(text=f"Level: {level}\nWords learnt: 0/{total_word_count}")
        show_frame(game_page)
        next_card()


level_complete = Frame(window)
level_complete.grid(row=0, column=0, sticky="nsew")

congrats_label = Label(level_complete, text="Congrats! You completed the level")
congrats_label.grid(row=0, column=1)

go_home = Button(level_complete, text="Home", command=home)
go_home.grid(row=1, column=0)

replay_level = Button(level_complete, text="Replay Level", command=replay)
replay_level.grid(row=1, column=1)

next_level_button = Button(level_complete, text="Next Level", command=next_level)
next_level_button.grid(row=1, column=2)

# ----------------------------- GAME PAGE -----------------------------------------------------------------------
def quit_game():
    show_frame(main_menu)

def play_audio(word):
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load(f"voices/{word}.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick()
    pygame.quit()

def next_card():
    global current_card, flip_timer, to_learn
    window.after_cancel(flip_timer)
    current_card = random.choice(to_learn)
    canvas.itemconfig(card_title, text="Korean", fill="black")
    canvas.itemconfig(card_word, text=current_card, fill="black")
    canvas.itemconfig(card_background, image=card_front_img)
    timer.grid(row=1, column=1)
    timer.set(1)
    unknown_button.grid_forget()
    known_button.grid_forget()
    flip_timer = window.after(6000, func=flip_card)
    decrease_timer()
    window.after(15, func=lambda: play_audio(current_card))

def flip_card():
    canvas.itemconfig(card_title, text="English", fill="white")
    # input_data = {
    #     'input_text': current_card
    # }
    # response = requests.post(url, json=input_data)
    # if response.status_code == 200:
    #     translated_text = response.json()['translation']
    #     canvas.itemconfig(card_word, text=translated_text, fill="white")
    # else:
    #     print('Error:', response.text)
    canvas.itemconfig(card_word, text="placeholder", fill="white")
    canvas.itemconfig(card_background, image=card_back_img)
    timer.grid_forget()
    hidden_label_2.grid(row=0, column=1, padx=80)
    unknown_button.grid(row=0, column=0)
    known_button.grid(row=0, column=2)


def is_known():
    to_learn.remove(current_card)
    print(len(to_learn))
    total_word_count = level_to_word[level]
    words_learnt = total_word_count - len(to_learn)
    stats_label.config(text=f"Level: {level}\nWords learnt: {words_learnt}/{total_word_count}")
    data_to_learn = pandas.DataFrame(to_learn)
    try:
        data_to_learn.to_sql(name=f"{save_to_load}", con=connection, schema="Korean nvarchar(30)", if_exists="replace", index=False)
    except sqlite3.OperationalError:
        show_frame(level_complete)
    else:
        next_card()


def decrease_timer():
    value = timer.get()
    if value > 0:
        new_value = value - 1/2300
        timer.set(new_value)
        window.after(1, decrease_timer)


game_page = Frame(window, bg=BACKGROUND_COLOR, padx=20, pady=20)
game_page.grid(row=0, column=0, sticky="nsew")

stats_frame = Frame(game_page, bg=BACKGROUND_COLOR)
stats_frame.grid(row=0, column=0)

card_frame = Frame(game_page)
card_frame.grid(row=1, column=0)

buttons_frame = Frame(game_page, bg=BACKGROUND_COLOR)
buttons_frame.grid(row=2, column=0)

flip_timer = window.after(5000, func=next_card)

canvas = Canvas(card_frame, width=500, height=329)
card_front_img = PhotoImage(file="images/card_2_front.png")
card_back_img = PhotoImage(file="images/card_2_back.png")
card_background = canvas.create_image(250, 164, image=card_front_img)
card_title = canvas.create_text(250, 110, text="", font=("Ariel", 30, "italic"))
card_word = canvas.create_text(250, 190, text="", font=("Ariel", 50, "bold"))
canvas.config(bg=BACKGROUND_COLOR, highlightthickness=0)
canvas.grid(row=0, column=0)

home_img = PhotoImage(file="images/home_2.png")
quit_button = Button(stats_frame, image=home_img, command=quit_game, borderwidth=0.5)
quit_button.grid(row=0, column=2)

cross_image = PhotoImage(file="images/wrong_button_2.png")
unknown_button = Button(buttons_frame, image=cross_image, highlightthickness=0, command=next_card, borderwidth=0)
unknown_button.grid(row=2, column=0)

check_image = PhotoImage(file="images/right_button_2.png")
known_button = Button(buttons_frame, image=check_image, highlightthickness=0, command=is_known, borderwidth=0)
known_button.grid(row=2, column=2)

timer = ctk.CTkProgressBar(buttons_frame, corner_radius=50, orientation="horizontal", fg_color="white", progress_color="green")
timer.grid(row=2, column=1)

stats_label = Label(stats_frame, text="", bg=BACKGROUND_COLOR, font=("", 10))
stats_label.grid(row=0, column=0)

hidden_label_1 = Label(stats_frame, text="", bg=BACKGROUND_COLOR)
hidden_label_1.grid(row=0, column=1, padx=150, pady=20)
hidden_label_2 = Label(buttons_frame, text="", bg=BACKGROUND_COLOR)

show_frame(main_menu)
window.mainloop()