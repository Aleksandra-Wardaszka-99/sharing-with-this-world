import cv2
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
import time
import glob
from tkinter import filedialog
import cv2
from pathlib import Path
from tkinter import *
import matplotlib
from matplotlib import cm 
import imageio.v2 as imageio  
from matplotlib.animation import FuncAnimation
from matplotlib.animation import PillowWriter


# Autor: A. Wardaszka
# Opis: pobranie plików .csv (*zmień w pliku matlab z .tsv na .csv aby ujednolicić format do powszechnie wykorzystywanego*) przez program,
# zaimportowanie zdj układu badanego i wyznaczenie trasy światłowodu, dla tych współrzędnych dane z pliku .csv są konwertowane na wartości
# koloru, a wartość barwy dopasowana do wartości min-max mniejszej od for now 300 - nie zarejestrowaną na razie większego odkształcenia
# aby uniknąć ustawienia granic z błedem - wygięcie wewnętrzne światłowodu wbudowanego i/lub końcówka bezodbiciowa może dać znacznie większe
# wartości i sfałszować skale. Są możliwości 3: zapisania .gif metodą wykorzystującą Funcanimation zawierającą zarówno zdj jak i ścieżkę światłowodu 
# zależną kolorystycznie od wartości zareejstrowanej, taki sam sposób dla pliku .mp4 metodą plt.ion czyli dynamiczną (użytkownik sam decyduje)
# jak również zwykle zilustrowanie wyników w postaci wykresu. Wynik dla 2. i 3. opcji można zapisać. Należy na wstępie przed puszczeniem animacji nadać 
# wymagane jest posiadanie pliku pomiarowego, np. z LUNA odisi, przekonwertowanie na .csv jeśli inny format 
# nazwę do plików by uniknąć błędu przy zapisie // jest to okno koło przycisku 
# pierwsza wersja: 30.11.2024
# ostatnia modyfikacja // dodanie wersji z Funcanimation oraz skalowanie // 23.05.2025



# tworzenie punktów i łączenie ich linią przy kliknięciu 
def click_event(event,x,y,flags,param):
    
    if event == cv2.EVENT_LBUTTONDOWN:
        cv2.circle(img,(x,y),3,(255,0,0),-1)
        points.append((x,y))
        if len(points) >= 2:
            cv2.line(img,points[-1],points[-2],(0,255,0),1)
        cv2.imshow("image", img)

# wybieranie ścieżki i wczytywanie z niej plików .csv
def path():
    csv_folder = filedialog.askdirectory(initialdir = "C:/<whatever>")
    path = glob.glob(csv_folder+"/*.csv")
    csv_list = []
    
    for files in path: 
        name = Path(files)
        print(name)
        csv_list.append(name)
        
    data['values'] =(csv_list)
    data.current(0)

# w obiekcie tk daje możliwość zmiany na następny/ poprzedni przy scrollowaniu     
def select_next(event):
    selection = filter.current()  
    last = len(filter['values']) - 1  
    key = event.keysym  
    if key == 'Up':
        try:
            filter.current(selection - 1)  
        except tk.TclError: 
            filter.current(last) 
    elif key == 'Down':
        try:  
            filter.current(selection + 1)  
        except tk.TclError:  
            filter.current(0)   
    return 'break'  


# załadowanie danych z wybranego pliku i wczytanie w współrzędne znalezione na obrazie w równiej odległości - obarczone błędem użytkowanika o czym trzeba pamiętać, przy bardziej 
# skolmplikowanych kształtach może wyrzucić błąd

def load_data(rowReader,array_for_picture_x,array_for_picture_y,x,y,il,heigh ):
    file = data.get()
    rowReader = pd.read_csv(file,sep=',', on_bad_lines='skip')
    rowReader = np.array(rowReader)
    il.append(rowReader.shape[1])
    heigh.append(rowReader.shape[0])
    suma = 0
    index = 0
    dist = []
    for jj in range(0,x.shape[0]-1):
        dist.append(((x[jj+1]-x[jj])**2 + (y[jj+1]-y[jj])**2)**0.5)
        suma = suma+dist[index]
        index = index+1

    lin_points = []
    for jj in range(0,x.shape[0]-1):
        lin_points.append(round((dist[jj]/suma)*il[0]))

    for jj in range(0,x.shape[0]-1):
        m1 =np.linspace(x[jj],x[jj+1],lin_points[jj])
        m2 = np.linspace(y[jj],y[jj+1],lin_points[jj])
        for zz in range(0,m1.shape[0]):
            array_for_picture_x.append(round(m1[zz]))
            array_for_picture_y.append(round(m2[zz]))
    
    print("finished")
        
# pierwsza możliwość wizualizacji wyników - wczytuje liste obrazów z już implementowanymi wartościami i wykreśla je w jednym oknie jako canvas, by następnie 
# zapisać do lsty w celu zapisania - funkcjonalność to wyświetlanie w czasie - na końcu zapisuje w wybranej przez użytkownika lokalizacji

def show_im(all_images):
    img_list_im=[]
    img_list_im,min_v,max_v = get_img_list()
    plt.ion()
    fig, ax = plt.subplots()
    fig.set_figheight(12)
    fig.set_figwidth(24)
    a1= ax.imshow(img_list_im[1], norm=matplotlib.colors.Normalize(vmin=min_v, vmax=max_v, clip=False),cmap='jet')
    c = plt.colorbar(a1)
    ind = 1
    ax.set_title("LUNA - visualisation", fontsize=20)
    for img in img_list_im:
            c.remove()
            # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            c = plt.colorbar(a1)
            a1=ax.imshow(img,norm=matplotlib.colors.Normalize(vmin=min_v, vmax=max_v, clip=False),cmap='jet')
            fig.canvas.draw()
            fig.canvas.flush_events()
            plt.savefig('frame.png') 
            all_images.append(imageio.imread('frame.png'))  
            time.sleep(0.1)
            procent = str(ind*100/(len(img_list_im)))
            print(procent+"%")
            ind=ind+1
      
    plt.show(block=False)  # Wyświetlenie wykresu w trybie nieblokującym  
    plt.pause(3)  # Czekaj 5 sekund  
    plt.close()

    path_vis = filedialog.askdirectory(initialdir = "C:/<whatever>")
    name = entry_vid.get()
    file_name = (path_vis+"\\"+name+".mp4")
    imageio.mimsave(file_name, all_images, fps=8)
    print("Animation -video - finished")

# zapisuje 

def vid_save(all_images):
    path = filedialog.askdirectory(initialdir = "C:/<whatever>")
    name = entry_vid.get()
    file_name = (path+"\\"+"LUNA "+name+".mp4")
    imageio.mimsave(file_name, all_images, fps=5)

# pobiera dane z rowreader, łącznie z współrzędnymi, wprowadza normalizacje wartości z pliku na barwy i dla każdej linijki wpisuje w obraz 
# w współrzędnych wyznaczonych na rysunku na początku. Jako min i max ustawia wartości znalezione na przestrzeni całego pliku // 
# zwraca listę z obrazami i wartości min i max pliku 
def get_img_list():
    img_list=[]
    file = data.get()
    
    rowReader = pd.read_csv(file,sep=',', on_bad_lines='skip')
    rowReader = np.array(rowReader)
    array_for_picture_x = []
    array_for_picture_y =[]
    img_list=[]
    il = []
    heigh = []
    all_colors = []
    
    load_data(rowReader, array_for_picture_x,array_for_picture_y,x,y,il,heigh)
    rowReader = np.array(rowReader)
    min_v = 0
    max_v = 0
    index_highest = 0
    for ii in  range(0,heigh[0]):
        for zz in  range(0,il[0]):
            if rowReader[ii][zz]<min_v:
                if rowReader[ii][zz]>-200:
                    min_v=rowReader[ii][zz]
            if rowReader[ii][zz]>max_v:
                    if rowReader[ii][zz]<200:
                        max_v = rowReader[ii][zz]

    norm = matplotlib.colors.Normalize(vmin=min_v, vmax=max_v, clip=False)
    mapper = cm.ScalarMappable(norm=norm, cmap=cm.jet)
    
    for jj in range(0,heigh[0]):
        img_copy = cv2.imread(imageFileName)
        img_copy = cv2.cvtColor(img_copy, cv2.COLOR_BGR2RGB)
        img_copy = cv2.resize(img_copy, (1200, 900))
        colors = [(r, g, b) for r, g, b, a in mapper.to_rgba(rowReader[jj], bytes=True)]
        colors = np.array(colors)
        for ii in range(0,il[0]):
            img_copy[(array_for_picture_y[ii]-5):(array_for_picture_y[ii]+5),(array_for_picture_x[ii]-5):(array_for_picture_x[ii]+5)] = colors[ii]

        img_list.append(img_copy)
    print(min_v)
    print(max_v)
    return img_list,min_v,max_v

# rysuje dane jako graph, zaczyna od wczytania, a następnie w trybie dynamicznym rysuje wykres i zapisuje do listy jako obraz, lista jest następnie zapisywana jako video 
def draw_chart(all_image_for_charts):
    all_image_for_charts = []
    file = data.get()
    rowReader = pd.read_csv(file,sep=',', on_bad_lines='skip')
    rowReader = np.array(rowReader)
    il=[]
    ind = []
    il.append(rowReader.shape[1])
    ind=rowReader.shape[0]
    plt.ion()

    fig = plt.figure()
    ax = fig.add_subplot(111)
    line1, = ax.plot(range(0,il[0]), rowReader[1])
    fig.set_figheight(12)
    fig.set_figwidth(24)
    plt.title("LUNA", fontsize=20)
    plt.xlabel("X-axis")
    plt.ylabel("Y-axis")
    
    for ii in range(0,ind):
        line1.set_xdata(range(0,il[0]))
        line1.set_ydata(rowReader[ii])
        fig.canvas.draw()
        fig.canvas.flush_events()
        plt.savefig('frame.png') 
        all_image_for_charts.append(imageio.imread('frame.png'))  
        time.sleep(0.1)
    path_chart = filedialog.askdirectory(initialdir = "C:/<whatever>")
    name = entry_chart.get()
    file_name = (path_chart+"\\"+"LUNA "+name+".mp4")
    imageio.mimsave(file_name, all_image_for_charts, fps=8)
    print("Animation -chart - finished")


# używając funkcji FuncAnimation, wykonuje funcję wizualizującą obraz z listy jako klatki i zapisuje go do pliku .gif ---> można wybrać inny format
def draw_visualisation():
    
    global img_list, min_v,max_v
    img_list=[]
    
    color_for_bar = []
    img_list,min_v,max_v=get_img_list()
    print(min_v)
    print(max_v)

    global fig_2 
    fig_2= plt.figure()
    global ax 
    ax= fig_2.add_subplot(111)
    fig_2.set_figheight(12)
    fig_2.set_figwidth(24)
    file = data.get()
    rowReader = pd.read_csv(file,sep=',', on_bad_lines='skip')
    rowReader = np.array(rowReader)
    a1=ax.imshow(img_list[1], norm=matplotlib.colors.Normalize(vmin=min_v, vmax=max_v, clip=False), cmap='jet')
    
    
    fig_2.colorbar(a1)
    ind = len(img_list) 
    # ind = ind-1
    print(ind)
    anim = FuncAnimation(fig = fig_2, func = animate, frames = ind, interval = 1, repeat = False)
    writergif = PillowWriter(fps=8)
    # path = filedialog.askdirectory(initialdir = "C:/<whatever>")
    name = entry_gif.get()
    file_name = "LUNA "+name+".gif"
    anim.save(file_name,writer=writergif)
    print("Animation finished - check .gif in your chosen folder")


# funkcja do animacji obrazu, informuje o progresie użytkownika
def animate(n):

    ax.imshow(img_list[n], norm=matplotlib.colors.Normalize(vmin=min_v, vmax=max_v, clip=False), cmap='jet')
    fig_2.canvas.draw()
    fig_2.canvas.flush_events()
    ax.set_title("LUNA", fontsize=20)
    ax.set_xlabel("X-axis")
    ax.set_ylabel("Y-axis")
    procent = str(n*100/(len(img_list)))
    print(procent+"%")
    
# zamyka aplikacje 
def exit():
    window.destroy()



# wczytanie danych np obrazu i rozplanowanie wyglądu app, typowa tk struktura 
imageFileName = input("enter the name of the image file: ")
img = cv2.imread(imageFileName)
img = cv2.resize(img, (1200, 900))
img_copy = cv2.imread(imageFileName)
img_copy = cv2.resize(img_copy, (1200, 900))
cv2.imshow("image",img)
points = []
cv2.setMouseCallback('image',click_event)
cv2.waitKey(0)
points = np.array(points)
x=[]
y=[]
x = points[:, 0]
y = points[:, 1]
x = np.array(x)
y = np.array(y)
all_images= []
all_charts =[]
all_image_for_charts = []
window = tk.Tk()
window.geometry('1120x210')
window.resizable(True, True)
window.title('LUNA')
window.config(bg="lightgrey")
s = ttk.Style()
s.configure('.', font=('Helvetica', 12))
plt.rcParams.update({'font.size': 12})    
button_path= ttk.Button(window, text ='Chose path',width = 50,command=lambda: path())
button_path.grid(row=0, column=0, padx=5, pady=5,sticky=W)



n2 = tk.StringVar()
data = ttk.Combobox(window,  width = 100, 
                        textvariable = n2)
data.bind('<Up>', select_next)  # up arrow
data.bind('<Down>', select_next)  # down arrow
data.grid(row=0, column=1, padx=5, pady=5,sticky=W)
img_list =[]
button_visual_gif= ttk.Button(window, text ='Show visualization for data/image for LUNA .csv - gif + saving',width = 68,command=lambda:draw_visualisation())
button_visual_gif.grid(row=1, column=1, padx=5, pady=5,sticky=W)

button_visual= ttk.Button(window, text ='Show visualization for data/image for LUNA .csv - imshow chain reaction',width = 68,command=lambda:show_im(all_images))
button_visual.grid(row=2, column=1, padx=5, pady=5, sticky=W)

button_chart= ttk.Button(window, text ='Show chart for data/image for LUNA .csv',width = 68,command=lambda:draw_chart(all_charts))
button_chart.grid(row=3, column=1, padx=5, pady=5, sticky=W)

name_var=tk.StringVar()
name_var.set("")
entry_gif = tk.Entry(window,textvariable = name_var, text ='Name for visual gif',width = 57, font=('calibre',11,'normal'))
entry_gif.grid(row=1, column=0,padx=5, pady=5,sticky=W)

name_vis2=tk.StringVar()
name_vis2.set("")
entry_vid = tk.Entry(window,textvariable = name_vis2, text ='Name for visual vid',width = 57, font=('calibre',11,'normal'))
entry_vid.grid(row=2, column=0,padx=5, pady=5,sticky=W)

name_img=tk.StringVar()
name_img.set("")
entry_chart = tk.Entry(window,textvariable = name_img, text ='Name for chart vid',width = 57, font=('calibre',11,'normal'))
entry_chart.grid(row=3, column=0,padx=5, pady=5,sticky=W)



button_exit= ttk.Button(window, text ='Exit program',width = 50,command=lambda: exit())
button_exit.grid(row=4, column=0,padx=5, pady=5,sticky=W)  


window.mainloop()


