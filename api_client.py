from tkinter import *
import customtkinter as ctk
from tkinter import messagebox
import pandas
import random
import sqlite3
import requests
import pygame

pygame.mixer.init()
connection = sqlite3.connect("vocabulary.db")
cursor = connection.cursor()
url = 'http://localhost:5000/translate'

korean_vocab = []

language_selected = ""
save = 0
level = 0
new_game = False
save_to_load = f"{language_selected}_save_{save}"
to_learn = []

BACKGROUND_COLOR = "#F4DED3"
current_card = ""


window = Tk()
window.title("Word Up")
window.config(padx=20, pady=20, bg=BACKGROUND_COLOR)
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
side = int(min(screen_height*0.65, screen_width*0.65))
window.minsize(width=side, height=side)
window.resizable(False, False)
window.grid_rowconfigure(0, weight=1)
window.grid_columnconfigure(0, weight=1)


# ----------------------------- MAIN MENU -------------------------------------------------------------------
def show_frame(page):
    page.tkraise()
    if page == game_page:
        print("Currently on game page")


def new_track():
    global new_game
    new_game = True
    show_frame(language_page)
    select_save_label.config(text="Select a save file to start:")


def load_track():
    show_frame(language_page)
    select_save_label.config(text="Select a save file to load:")


def continue_track():
    global save_to_load, to_learn
    with open("data/recent_save.txt", 'r') as file_1:
        save_to_load = file_1.read()
    cursor.execute(f"select * from saves_list where save_name = '{save_to_load}'")
    records = cursor.fetchall()
    level_to_set = records[0][1]
    stats_label.config(text=f"Level: {level_to_set}")
    cursor.execute(f"select * from {save_to_load}")
    word_list = cursor.fetchall()
    to_learn = [tup[0] for tup in word_list]
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

fr_button_img = PhotoImage(file="images/french_button.png")
french_button = Button(language_page, image=fr_button_img, command=lambda: load_pages("French"), borderwidth=0)
sp_button_img = PhotoImage(file="images/spanish_button.png")
spanish_button = Button(language_page, image=sp_button_img, command=lambda: load_pages("Spanish"), borderwidth=0)
ko_button_img = PhotoImage(file="images/korean_button.png")
korean_button = Button(language_page, image=ko_button_img, command=lambda: load_pages("Korean"), borderwidth=0)

french_button.grid(row=1, column=0)
spanish_button.grid(row=2, column=0)
korean_button.grid(row=3, column=0)


# ----------------------------- SAVE SELECT PAGE ----------------------------------------------------------------
def delete_save(save_to_delete):
    cursor.execute(f"drop table {save_to_delete}")
    cursor.execute(f"delete from saves_list where save_name = '{save_to_load}'")


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
    global save, save_to_load, to_learn
    save = n
    save_to_load = f"{language_selected}_save_{save}"
    cursor.execute(f"select * from saves_list where save_name = '{save_to_load}'")
    records = cursor.fetchall()
    level_to_set = records[0][1]
    stats_label.config(text=f"Level: {level_to_set}")
    cursor.execute(f"select * from {save_to_load}")
    word_list = cursor.fetchall()
    to_learn = [tup[0] for tup in word_list]
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

saves_page_title = Label(saves_page, text="", bg="green", fg="white", font=("", 36))
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
    show_frame(game_page)
    stats_label.config(text=f"Level: {n}")
    cursor.execute(f"update saves_list set level = {n} where save_name = '{save_to_load}'")
    cursor.execute(f"select * from korean_full")
    records = cursor.fetchall()
    word_count = level_to_word[n]
    to_learn = [tup[0] for tup in records][0:word_count]
    next_card()


levels_page = Frame(window)
levels_page.grid(row=0, column=0, sticky="nsew")

levels_page.grid_rowconfigure(0, weight=0)
levels_page.grid_rowconfigure(1, weight=1)
levels_page.grid_rowconfigure(2, weight=1)
levels_page.grid_columnconfigure(0, weight=1)

levels_page_title = Label(levels_page, text="", bg="green", fg="white", font=("", 36))
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
        width=8, height=2, borderwidth=0,
        command=lambda j=i: load_level_n(j+1)
    )
    button_i.grid(row=row_n, column=column_n, padx=10, pady=10)
    column_n = (column_n + 1) % 4
    if column_n == 0:
        row_n += 1


# ----------------------------- GAME PAGE -----------------------------------------------------------------------
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
    flip_timer = window.after(5000, func=flip_card)
    decrease_timer()


def flip_card():
    canvas.itemconfig(card_title, text="English", fill="white")
    input_data = {
        'input_text': current_card
    }
    response = requests.post(url, json=input_data)
    if response.status_code == 200:
        translated_text = response.json()['translation']
        canvas.itemconfig(card_word, text=translated_text, fill="white")
    else:
        print('Error:', response.text)
    canvas.itemconfig(card_background, image=card_back_img)
    timer.grid_forget()
    unknown_button.grid(row=1, column=0)
    known_button.grid(row=1, column=2)


def is_known():
    to_learn.remove(current_card)
    print(len(to_learn))
    data_to_learn = pandas.DataFrame(to_learn)
    data_to_learn.to_sql(name=f"{save_to_load}", con=connection, schema="Korean nvarchar(30)", if_exists="replace", index=False)
    next_card()


def decrease_timer():
    value = timer.get()
    if value > 0:
        new_value = value - 1/2800
        timer.set(new_value)
        window.after(1, decrease_timer)


game_page = Frame(window, bg=BACKGROUND_COLOR)
game_page.grid(row=0, column=0, sticky="nsew")

game_page_title = Label(game_page, text="GAME RUNNING")
game_page_title.grid(row=0, column=1)

stats_label = Label(game_page, text="GAME")
stats_label.grid(row=2, column=1)

flip_timer = window.after(5000, func=next_card)

canvas = Canvas(game_page, width=500, height=329)
card_front_img = PhotoImage(file="images/card_1_front.png")
card_back_img = PhotoImage(file="images/card_1_back.png")
card_background = canvas.create_image(250, 164, image=card_front_img)
card_title = canvas.create_text(250, 110, text="", font=("Ariel", 30, "italic"))
card_word = canvas.create_text(250, 190, text="", font=("Ariel", 50, "bold"))
canvas.config(bg=BACKGROUND_COLOR, highlightthickness=0)
canvas.grid(row=0, column=0, columnspan=3)

cross_image = PhotoImage(file="images/wrong.png")
unknown_button = Button(game_page, image=cross_image, highlightthickness=0, command=next_card)
unknown_button.grid(row=1, column=0)

check_image = PhotoImage(file="images/right.png")
known_button = Button(game_page, image=check_image, highlightthickness=0, command=is_known)
known_button.grid(row=1, column=2)

timer = ctk.CTkProgressBar(game_page, corner_radius=50, orientation="horizontal", fg_color="white", progress_color="green")
timer.grid(row=1, column=1)

show_frame(main_menu)
window.mainloop()