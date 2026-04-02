from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk

root = Tk()
root.title("MIBOMBO")

# Charger et redimensionner l'image
img = Image.open("logo.png")
img = img.resize((120, 120))  # taille du logo affiché
logo = ImageTk.PhotoImage(img)

# Icône (petite automatiquement)
root.iconphoto(True, logo)

# Logo en haut
label_logo = Label(root, image=logo)
label_logo.image = logo
label_logo.grid(row=0, column=0, pady=10)

# Bouton en dessous
ttk.Button(root, text="Hello World").grid(row=1, column=0)

root.state("zoomed")
root.mainloop()