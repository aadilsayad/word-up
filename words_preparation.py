with open("data/korean_unformatted.txt", 'r', encoding='utf-8') as file:
    lines = file.readlines()

with open("data/korean_words.txt", 'w', encoding='utf-8') as file_1:
    for line in lines:
        word = line.split()[0]
        file_1.write(word + '\n')

saves_list_table = {
    korean_save_1: 15,
    korean_save_2: 30,
    spanish_save_3: 60
}