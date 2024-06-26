import tkinter as tk
from tkinter import scrolledtext
from tkinter.filedialog import asksaveasfile
import sys
from time import localtime, strftime
import asyncio
import helper
import threading
from localisation import default


L = default['app']  # Default language


class StdoutRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.write(f"{L['welcome']} {strftime('%H:%M:%S', localtime())}.\n")

    def write(self, string):
        self.text_widget.config(state='normal')
        self.text_widget.insert("end", string)
        self.text_widget.see("end")  # Scroll to the end
        self.text_widget.config(state='disabled')

    def flush(self):
        return None


def start():
    name = entry_name.get()
    surname = entry_surname.get()
    patronymic = entry_patronymic.get()
    person = ' '.join([surname, name, patronymic]).strip()
    wiki_info = helper.wikisearch(person=person, verbosity=True)
    higeo_info = helper.higeosearch(person=person, verbosity=True)
    rsl_data = asyncio.run(helper.rslsearch(person=person, verbosity=True, parallel=True))
    geokniga_data = helper.geoknigasearch(person=person, verbosity=True)
    rgo_data = asyncio.run(helper.rgo_check(name=person))
    rnb_data = asyncio.run(helper.rnb_check(name=person))  # pics
    nnr_data = asyncio.run(helper.nnr_check(name=person))
    spb_data = asyncio.run(helper.spb_check(name=person))

    lines = []
    if wiki_info is not None:
        lines.append(L['wiki_info'])
        lines.append(f"{L['date_of_birth']}{wiki_info[0]} ; {L['date_of_death']}{wiki_info[1]}\n")
        lines.append(f"{L['place_of_birth']}{wiki_info[2]} ; {L['description']}{wiki_info[4]}\n")
        lines.append(f"{L['place_of_death']}{wiki_info[3]} ; {L['description']}{wiki_info[5]}\n")
        lines.append('\n\n\n\n')
    lines.append(f"{L['exists_in_higeo']}{higeo_info}")
    lines.append('\n\n\n\n')
    lines.append(L['bibliographical_info'])
    if rsl_data is not None:
        lines.append(L['rsl_data'])
        lines.append('\n'.join(map(str, rsl_data)))
        lines.append('\n\n')
    if geokniga_data is not None:
        lines.append(L['geokniga_data'])
        lines.append('\n'.join(map(str, geokniga_data)))
        lines.append('\n\n')

    if rgo_data is not None:
        lines.append(L['rgo_data'])
        lines.append('\n'.join(rgo_data))
        lines.append('\n\n')
    if nnr_data is not None:
        lines.append(L['nnr_data'])
        lines.append('\n'.join([i[0] for i in nnr_data[1]['Публикации ']]))
        lines.append('\n\n')
    if spb_data is not None:
        lines.append(L['spb_data'])
        lines.append('\n'.join(spb_data[0]))
        lines.append('\n\n')
    if rnb_data is not None:
        lines.append(L['rnb_card_images'])
        lines.append('\n'.join([f"{key}:   {value}" for key, value in rnb_data.items()]))
        lines.append('\n\n')
    file_save(lines)


def update_button_text(percentage=None):
    if percentage is None:
        start_button.config(text=L['start'])
    else:
        start_button.config(text=f"{L['start']} ({percentage}%)")


def file_save(text):
    f = asksaveasfile(mode='w', defaultextension=".txt")
    if f is None:
        return

    with open(f.name, 'w', encoding="utf-8") as realfile:
        realfile.writelines(text)
    f.close()


root = tk.Tk()
root.title("Bibliomaker")
root.resizable(False, False)

tk.Label(root, text=L['surname']).grid(row=0, column=0)
entry_surname = tk.Entry(root)
entry_surname.grid(row=0, column=1)

tk.Label(root, text=L['name']).grid(row=1, column=0)
entry_name = tk.Entry(root)
entry_name.grid(row=1, column=1)

tk.Label(root, text=L['patronymic']).grid(row=2, column=0)
entry_patronymic = tk.Entry(root)
entry_patronymic.grid(row=2, column=1)

tk.Label(root, text=L['keywords']).grid(row=3, column=0)
entry_fields_of_work = tk.Entry(root, state='disabled')
entry_fields_of_work.grid(row=3, column=1)

t = threading.Thread(target=start, name="Start")
t.daemon = True

start_button = tk.Button(root, text=L['start'], command=lambda: t.start())
start_button.grid(row=4, columnspan=2)

# For Logs
logs = scrolledtext.ScrolledText(root, width=40, height=10)
sys.stdout = StdoutRedirector(logs)
logs.grid(columnspan=2)

root.mainloop()
