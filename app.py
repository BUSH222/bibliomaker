import tkinter as tk
from tkinter import scrolledtext
from tkinter.filedialog import asksaveasfile
import sys
from time import localtime, strftime
import asyncio
import helper1 as h
import helper2 as h2
import threading


class StdoutRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.write(f"Welcome to bibliomaker!\nRight now it is {strftime('%H:%M:%S', localtime())}.\n")

    def write(self, string):
        self.text_widget.config(state='normal')
        self.text_widget.insert("end", string)
        self.text_widget.see("end")  # Scroll to the end
        self.text_widget.config(state='disabled')


def start():
    name = entry_name.get()
    surname = entry_surname.get()
    patronymic = entry_patronymic.get()
    person = ' '.join([surname, name, patronymic]).strip()
    wiki_info = h.wikisearch(person=person, verbosity=True)
    higeo_info = h.higeosearch(person=person, verbosity=True)
    rsl_data = asyncio.run(h.rslsearch(person=person, verbosity=True, parallel=True))
    geokniga_data = h.geoknigasearch(person=person, verbosity=True)
    rgo_data = h2.rgo_check(name=person)
    rnb_data = h2.rnb_check(name=person)  # pics
    nnr_data = h2.nnr_check(name=person)
    spb_data = h2.spb_check(name=person)

    lines = []
    if wiki_info is not None:
        lines.append('Wikipedia information found:\n')
        lines.append(f'Date of Birth: {wiki_info[0]} ; Date of death: {wiki_info[1]}\n')
        lines.append(f'Place of Birth: {wiki_info[2]} ; Description: {wiki_info[4]}\n')
        lines.append(f'Place of Death: {wiki_info[3]} ; Description: {wiki_info[5]}\n')
        lines.append('\n\n\n\n')
    lines.append(f'Person exists in the higeo database: {higeo_info}')
    lines.append('\n\n\n\n')
    lines.append('Bibliographical info:\n\n')
    if rsl_data is not None:
        lines.append('RSL Data:\n')
        lines.append('\n'.join(map(str, rsl_data)))
        lines.append('\n\n')
    if geokniga_data is not None:
        lines.append('Geokniga Data:\n')
        lines.append('\n'.join(map(str, geokniga_data)))
        lines.append('\n\n')

    if rgo_data is not None:
        lines.append('RGO Data:\n')
        lines.append('\n'.join(rgo_data))
        lines.append('\n\n')
    if nnr_data is not None:
        lines.append('NNR Data:\n')
        lines.append('\n'.join([i[0] for i in nnr_data[1]['Публикации ']]))
        lines.append('\n\n')
    if spb_data is not None:
        lines.append('SPB Data:\n')
        lines.append('\n'.join(spb_data[1]))
        lines.append('\n\n')
    if rnb_data is not None:
        lines.append('RNB Card Images:\n')
        lines.append('\n'.join([f'{key}:   {value}' for key, value in rnb_data.items()]))
        lines.append('\n\n')
    file_save(lines)


def update_button_text(percentage=None):
    if percentage is None:
        start_button.config(text="Start")
    else:
        start_button.config(text=f"Start ({percentage}%)")


def file_save(text):
    f = asksaveasfile(mode='w', defaultextension=".txt")
    if f is None:
        return
    f.writelines(text)
    f.close()


root = tk.Tk()
root.title("Bibliomaker")
root.resizable(False, False)

tk.Label(root, text="Name").grid(row=0, column=0)
entry_name = tk.Entry(root)
entry_name.grid(row=0, column=1)

tk.Label(root, text="Surname").grid(row=1, column=0)
entry_surname = tk.Entry(root)
entry_surname.grid(row=1, column=1)

tk.Label(root, text="Patronymic").grid(row=2, column=0)
entry_patronymic = tk.Entry(root)
entry_patronymic.grid(row=2, column=1)

tk.Label(root, text="Keywords").grid(row=3, column=0)
entry_fields_of_work = tk.Entry(root)
entry_fields_of_work.grid(row=3, column=1)

t = threading.Thread(target=start, name="Start")
t.daemon = True

start_button = tk.Button(root, text="Start", command=lambda: t.start())
start_button.grid(row=4, columnspan=2)

# For Logs
logs = scrolledtext.ScrolledText(root, width=40, height=10)
sys.stdout = StdoutRedirector(logs)
logs.grid(columnspan=2)

root.mainloop()
