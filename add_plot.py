import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
import glob
from tkinter import filedialog
from pathlib import Path
from tkinter import *
import math
import mplcursors
import os
import pathlib
import cv2

# Autor: A. Wardaszka
# Opis: Program z interferjsem graficznym. Użytkownik wybiera po naciśnieciu przycisku "Chose path" ścieżkę do pobrania plików .csv 
# ścieżka może być wielokrotnie zmieniana podczas wizualizacji danych na wykresie bez kasowania poprzednich, parametry przedstawiane są 
# z listy "Chose type of chart" która jest stała. Wybrana nazwa pliku z "Chose path" określa, na których danych przeprowadzane są działania
# "Show chart" wyświetla okno z wykresem - wyłączona jest funkcja jego zamknięcia /// polecane jest w przyszłości adjustacja wielkości okna 
# "Add chosen parameter" dodaje określony parametr danych do wykresu, a "Clear plot" kasuje wszystkie zapisane wykresy z subplots pozwalając na 
# rozpoczęcie procesu od nowa. Dane dla danego pliku mogą być niezależnie zapisane w formacie .xlsx. Parametry początkowe i końcowe dla osi wykresu 
# mogą być ustawianie poprzez wpisane wartości całkowitej w "Min freq" "Max freq" "Min value" "Max value". Zamknięcie programu następuje bo 
# wciśnieciu przycisku "Exit"
# pierwsza skończona wersja: 18.02.2025
#  modyfikacja // uniemożliwienie wyłączenia okna wykresu (X) // 17.09.2025


global cursor 
global cursor2 
global cursor3
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

# def exit(event):
   
#     key = event.keysym  
#     if key == 'Esp':
        


def readfile_csv(file,freq,E,Eloss,M,Mloss,Ecomplex,Mcomplex):

    df1 = []
    df2 = []
    df3 = []
    df4 = []
    df5 = []
    
    line_number = 14
    rowReader = pd.read_csv(file,delimiter= ',', on_bad_lines='skip', skiprows=line_number)
    rowReader = np.array(rowReader)
  
    for row in rowReader:
        df1.append(row[0])
        df2.append(row[1])
        df3.append(row[2])
        df4.append(row[3])
        df5.append(row[4])
    df1 = np.array(df1)
    df2 = np.array(df2)
    df3 = np.array(df3)
    df4 = np.array(df4)
    df5 = np.array(df5)
    for i in range(len(df1)):
        freq.append(df1[i])
        E.append(df2[i])
        Eloss.append(df3[i])
        M.append(df4[i])
        Mloss.append(df5[i])
    
    freq = np.array(freq)  
    E = np.array(E)  
    M = np.array(M)  
    Eloss = np.array(Eloss)  
    Mloss = np.array(Mloss) 
    for i in range(len(E)):
        
        Ecomplex.append(complex(E[i],Eloss[i]))
        Mcomplex.append(complex(M[i],Mloss[i]))
    Ecomplex = np.array(Ecomplex) 
    Mcomplex = np.array(Mcomplex) 

def calculate_SE(freq,E,Eloss,M,Mloss, SE,Mcomplex,Cond_AC):

    E0 = 8.854 * (10 ** -12)
    M0 = 4 * np.pi * (10 ** -7)
    skin_depth = []
    b1 = []
    for i in range(len(Eloss)):
        Cond_AC.append(2 * np.pi * freq[i] * Eloss[i]*E0)
    Cond_AC = np.array(Cond_AC) 
    for i in range(len(Eloss)):
        skin_depth.append(np.sqrt(1/(np.absolute(np.pi * freq[i] * M[i] * M0* Cond_AC[i]))))
    print(len(Cond_AC))
    skin_depth = np.array(skin_depth) 
    for i in range(len(Eloss)):
        b1.append(20 * np.log10(math.e**(0.003 / skin_depth[i])))
    b1 = np.array(b1) 
    for i in range(len(Eloss)):
        SE.append(20 * np.log10(np.sqrt(Cond_AC[i] / (2 * np.pi * freq[i] *E0* M[i]))*0.25) + b1[i])
        #SE.append((-10*np.log10(Cond_AC[i]/(32 * np.pi * freq[i]*E0*M[i])))-8.68*0.003*np.sqrt(Cond_AC[i]*2 * np.pi * freq[i]*M[i]*0.5))
        #SE.append(-5-(39.5+10*np.sqrt(np.log10(Cond_AC[i]/(2 * np.pi * freq[i]* Mcomplex[i] * M0))))+(8.7*0.003*np.sqrt(np.pi*freq[i]* Mcomplex[i] * M0*Cond_AC[i])))
        
        #SE.append(3.34*0.003*np.sqrt(freq[i] * Mcomplex[i] * M0 * Cond_AC[i])+168-10*np.log10((freq[i]*Mcomplex[i]*M0)/Cond_AC[i]))
    SE = np.array(SE) 

def calculate_RL(freq,E,Eloss,M,Mloss,RL,coefficient_reflection,input_impedance,Ecomplex,Mcomplex,coefficient_transmission):
    E0 = 8.854 * (10 ** -12)
    M0 = 4 * np.pi * (10 ** -7)
    k=[]
    A1 = []
    for i in range(len(Ecomplex)):
        A1.append(Mcomplex[i] / Ecomplex[i])
   
    A1 = np.array(A1) 
 
    for i in range(len(Ecomplex)):
        input_impedance.append(np.sqrt(A1[i])*1j*np.tanh(2 * np.pi * np.sqrt(Mcomplex[i] * Ecomplex[i]) * freq[i] * 0.003))
        k.append(2 * np.pi*freq[i]*np.sqrt(E[i]*E0*M0*M[i]))
        
    input_impedance = np.array(input_impedance)
    for i in range(len(input_impedance)):
        #RL.append(20 * np.log10(np.abs(input_impedance[i]/(np.sqrt(M0/E0)) - 1) / np.abs(input_impedance[i]/(np.sqrt(M0/E0)) + 1)))
        coefficient_reflection.append(abs((np.sqrt(M[i]/E[i])-1)/(np.sqrt(M[i]/E[i])+1)))
        # if k[i] > 1:
        #     coefficient_reflection.append(abs(k[i]-(np.sqrt(k[i]*k[i]-1))))
        # else:
        #     coefficient_reflection.append(abs(k[i]+(np.sqrt(k[i]*k[i]-1))))
        coefficient_transmission.append(1/(math.e**((np.sqrt(Mcomplex[i]/Ecomplex[i])*(2 * np.pi*freq[i]*0.003)/300000000))))
 
    coefficient_reflection = np.array(coefficient_reflection)
    coefficient_transmission = np.array(coefficient_transmission)
    for i in range(len(input_impedance)):
         RL.append(20 * np.log10(coefficient_reflection[i]))
    RL = np.array(RL)
    #input_impedance = np.sqrt(A1)*1j*np.tanh(2 * np.pi * np.sqrt(A1) * freq * 3)
    #RL = 20 * np.log10(np.abs(input_impedance - 1) / np.abs(input_impedance + 1))
    #coefficient_reflection = (input_impedance / (120 * np.pi) - 1) / (input_impedance / (120 * np.pi) + 1)
   

def calculate_loss_tangens(freq,E,Eloss,M,Mloss,tangens_M,tangens_E):
    for i in range(len(E)):
        tangens_E.append((Eloss[i] / E[i]))
        tangens_M.append((Mloss[i] / M[i]))
    tangens_E = np.array(tangens_E)
    tangens_M = np.array(tangens_M)


def cursor1_annotations(sel):
    sel.annotation.set_text(
        'Cursor One:\n x {:.2f} \n y {:.2f} '.format(sel.target[0], sel.target[1]))
    sel.annotation.get_bbox_patch().set(fc="powderblue", alpha=0.9)
   

            
def add_plot(ax_chart, charts_name):
    
    EM_parameter  = filter.get()
    
    file  = (path_way.cget("text")+"/"+data.get()+'.csv')   

    freq_min = spin.get()
    freq_max = spin_2.get()
    freq_min = int(freq_min)
    freq_max = int(freq_max)
    
    val_min = spiny.get()
    val_max = spin_y2.get()
    val_min = int(val_min)
    val_max = int(val_max)
    
    Ecomplex = []
    Mcomplex = []
    freq = []
    E= []
    Eloss = []
    M=[]
    RL = []
    SE = []
    tangens_M = []
    tangens_E = []
    Mloss=[]
    coefficient_reflection = []
    Cond_AC=[]
    input_impedance = []
    coefficient_transmission = []
    data_name_1 = Path(file).stem
    readfile_csv(file, freq,E,Eloss,M,Mloss,Ecomplex,Mcomplex)
    calculate_RL(freq,E,Eloss,M,Mloss,RL,coefficient_reflection,input_impedance,Ecomplex,Mcomplex,coefficient_transmission)
    calculate_SE(freq,E,Eloss,M,Mloss, SE,Mcomplex,Cond_AC)
    calculate_loss_tangens(freq,E,Eloss,M,Mloss,tangens_M,tangens_E)

    if EM_parameter == "RL":
        ax_chart.plot(freq, RL)
        D_name = (data_name_1+"_RL")
        ax_chart.set(xlabel='Frequency [Hz]', ylabel='RL [dB]')
        charts_name.append(D_name)
        print(D_name)

    if EM_parameter == "SE":
        ax_chart.plot(freq, SE)
        D_name = (data_name_1+"_SE")
        ax_chart.set(xlabel='Frequency [Hz]', ylabel='SE [dB]')
        charts_name.append(D_name)
        print(D_name)

    if EM_parameter == "coefficient_transmission":
        ax_chart.plot(freq, coefficient_transmission)
        D_name = (data_name_1+"_coefficient_transmission")
        ax_chart.set(xlabel='Frequency [Hz]', ylabel='coefficient_transmission')
        charts_name.append(D_name)
        print(D_name)

    if EM_parameter == "Conductivity":
        
        ax_chart.plot(freq, Cond_AC)
        D_name = (data_name_1+"_Conductivity")
        ax_chart.set(xlabel='Frequency [Hz]', ylabel='Conductivity')
        charts_name.append(D_name)
        print(D_name)

    if EM_parameter == "tangens_M":
        
        ax_chart.plot(freq, tangens_M)
        D_name = (data_name_1+"_tangens_M")
        ax_chart.set(xlabel='Frequency [Hz]', ylabel='tangens_M')
        charts_name.append(D_name)
        print(D_name)

    if EM_parameter == "tangens_E":
        
        ax_chart.plot(freq, tangens_E)
        D_name = (data_name_1+"_tangens_E")
        ax_chart.set(xlabel='Frequency [Hz]', ylabel='tangens_E')
        charts_name.append(D_name)
        print(D_name)

    if EM_parameter == "E`":
        ax_chart.plot(freq, E)
        D_name = (data_name_1+"_E`")
        ax_chart.set(xlabel='Frequency [Hz]', ylabel='Permittivity_real')
        charts_name.append(D_name)
        print(D_name)
        
    if EM_parameter == "E``":
        ax_chart.plot(freq, Eloss)
        D_name = (data_name_1+"_E``")
        ax_chart.set(xlabel='Frequency [Hz]', ylabel='Permittivity_imag')
        charts_name.append(D_name)
        print(D_name)

    if EM_parameter == "M`":
        ax_chart.plot(freq, M)
        D_name = (data_name_1+"_M`")
        ax_chart.set(xlabel='Frequency [Hz]', ylabel='Permeability_real')
        charts_name.append(D_name)
        print(D_name)

    if EM_parameter == "M``":
        
        ax_chart.plot(freq, Mloss)
        D_name = (data_name_1+"_M``")
        ax_chart.set(xlabel='Frequency [Hz]', ylabel='Permeability_imag')
        charts_name.append(D_name)
        print(D_name)
    if EM_parameter == "coefficient_reflection":
        
        ax_chart.plot(freq, coefficient_reflection)
        D_name = (data_name_1+"_coefficient_reflection")
        ax_chart.set(xlabel='Frequency [Hz]', ylabel='coefficient_reflection')
        charts_name.append(D_name)
        print(D_name)
        


def save_to_file():
    path_to_save = filedialog.askdirectory(initialdir = "C:/<whatever>")
    file  = (path_way.cget("text")+"/"+data.get()+'.csv')
    
    Ecomplex = []
    Mcomplex = []
    freq = []
    E= []
    Eloss = []
    M=[]
    RL = []
    SE = []
    tangens_M = []
    tangens_E = []
    Mloss=[]
    coefficient_reflection = []
    input_impedance = []
    coefficient_transmission=[]
    data_name_1 = Path(file).stem
    Cond_AC=[]
   

    readfile_csv(file,freq,E,Eloss,M,Mloss,Ecomplex,Mcomplex)
    calculate_RL(freq,E,Eloss,M,Mloss,RL,coefficient_reflection,input_impedance,Ecomplex,Mcomplex,coefficient_transmission)
    calculate_loss_tangens(freq,E,Eloss,M,Mloss,tangens_M,tangens_E)
    calculate_SE(freq,E,Eloss,M,Mloss, SE,Mcomplex,Cond_AC)


    name = entry.get()
    file_name = (path_to_save+"\\"+name+".xlsx")
    writer = pd.ExcelWriter(file_name, engine='openpyxl') 
    wb  = writer.book
    df = pd.DataFrame({
                  'freq': freq,
                  'E`': E,
                  'E``': Eloss,
                  'M`': M,
                  'M``': Mloss,
                  'Return Loss': RL,
                  'Shielding Emission': SE,
                  'Zin impedance': input_impedance,
                  'Conductivity': Cond_AC,
                  'coefficient_transmission':coefficient_transmission,
                  'coefficient_reflection':coefficient_reflection,
                  'Ecomplex':Ecomplex,
                  'Mcomplex':Mcomplex,
                  'tangens_E': tangens_E,
                  'tangens_M': tangens_M
                  })
    
    df.to_excel(writer, sheet_name=data_name_1,index=False)
    wb.save(file_name)

def path():
    csv_folder = filedialog.askdirectory(initialdir = "C:/<whatever>")   
    path_way.config(text=csv_folder)
    path = glob.glob(csv_folder+"/*.csv")   
    csv_list = []
    
    print(path_way)

    for files in path: 
        name = Path(files).stem
        print(name)
        csv_list.append(name)
    data['values'] =(csv_list)
    data.current(0)
    
      
      
def exit():
    window.destroy()

def show_plot(ax_chart):
    # if plt.figure is False:
    #     fig=plt.figure()
    #     fig.add_axes(ax_chart)
    freq_min = spin.get()
    freq_max = spin_2.get()
    freq_min = int(freq_min)
    freq_max = int(freq_max)
    val_min = spiny.get()
    val_max = spin_y2.get()
    val_min = int(val_min)
    val_max = int(val_max)
    ax_chart.set_xlim([freq_min, freq_max])
    ax_chart.set_ylim([val_min, val_max])
    ax_chart.legend(charts_name)
    cursor = mplcursors.cursor(ax_chart, hover=False)
    cursor.connect('add', cursor1_annotations)
    fig.show()

    




def clear_plot(ax_chart,charts_name):
    ax_chart.clear()
    ax_chart.grid()
    charts_name.clear()
    print(charts_name)



print("HYDEF")

window = tk.Tk()
window.geometry('750x450')
window.resizable(True, True)
window.title('HYDEF charts')
window.config(bg="lightgrey")
s = ttk.Style()
s.configure('.', font=('Helvetica', 14))
plt.rcParams.update({'font.size': 18})       
label = ttk.Label(window,width = 20, text = "Choose type of chart :")
label.grid(row=0, column=0, padx=5, pady=5)
n = tk.StringVar()
filter = ttk.Combobox(window, width = 50, font=('Helvetica', 12) ,
                        textvariable = n)
filter['values'] = ('RL',
                    'SE',
                    'coefficient_transmission',
                    'coefficient_reflection',
                    'Conductivity',
                    'tangens_E',
                    'tangens_M',
                    'E`',
                    'E``',
                    'M`',
                    'M``')
filter.grid(row=0, column=1, padx=5, pady=5,sticky=W)
filter.current(0)
filter.bind('<Up>', select_next)  # up arrow
filter.bind('<Down>', select_next)  # down arrow

#check

path_way = ttk.Label(window,  width = 20,  font=('Helvetica', 12),
                        text = "")
# path_way.grid(row=1, column=2, padx=5, pady=5)



n2 = tk.StringVar()
data = ttk.Combobox(window,  width = 50,  font=('Helvetica', 12),
                        textvariable = n2)

img = cv2.imread("C://Users//AleksandraWardaszka//Desktop//50 x 50 mm logo ITWL.png")
cv2.imwrite("itwl.png", img)
data.bind('<Up>', select_next)  # up arrow
data.bind('<Down>', select_next)  # down arrow
data.grid(row=1, column=1, padx=5, pady=5, sticky=W)

fig, ax_chart = plt.subplots()
fig.set_figheight(6)
fig.set_figwidth(12)
charts_name = []
plt.grid()
win = plt.gcf().canvas.manager.window
win.overrideredirect(True)
win.geometry("{0}x{1}".format(win.winfo_screenwidth(), win.winfo_screenheight()))


button_path= ttk.Button(window, text ='Chose path',width = 20,command=lambda: path())
button_path.grid(row=1, column=0, padx=5, pady=5)



button_read= ttk.Button(window, text ='Add chosen parameter',width = 20,command=lambda: add_plot(ax_chart,charts_name))
button_read.grid(row=2, column=0,padx=5, pady=5)

button_all= ttk.Button(window, text ='Show chart',width = 50,command=lambda: show_plot(ax_chart))
button_all.grid(row=2, column=1,padx=5, pady=5, sticky=W)

label_datafiles = ttk.Label(window,  width = 20, text = "Choose safe file name:")
label_datafiles.grid(row=4, column=0,padx=5, pady=5)

name_var=tk.StringVar()
name_var.set("")
entry = tk.Entry(window,textvariable = name_var, text ='Save data',width = 40,  font=('Helvetica', 12))
entry.grid(row=4, column=1,padx=5, pady=5,sticky=W)

button_clear= ttk.Button(window, text ='Clear plot',width = 20,command=lambda: clear_plot(ax_chart,charts_name))
button_clear.grid(row=3, column=0,padx=5, pady=5)



button_save= ttk.Button(window, text ='Save data',width = 20,command=lambda: save_to_file())
button_save.grid(row=5, column=0,padx=5, pady=5)

button_exit= ttk.Button(window, text ='Exit program',width = 20,command=lambda: exit())
button_exit.grid(row=10, column=0,padx=5, pady=5)

label_x1 = ttk.Label(window,width = 20, text = "Min freq:")
label_x1.grid(row=6, column=0, padx=5, pady=5)

t1 = tk.IntVar(window,0)
t2 = tk.IntVar(window,18000000000)

spin = ttk.Spinbox(window, width = 50, font=('Helvetica', 12),from_= 0, to = 18000000000, textvariable=t1)    
spin.grid(row=6, column=1, padx=5, pady=5,sticky=W)  


label_x2 = ttk.Label(window,width = 20, text = "Max freq:")
label_x2.grid(row=7, column=0, padx=5, pady=5)

spin_2 = ttk.Spinbox(window, width = 50, font=('Helvetica', 12),from_= 0, to = 18000000000, textvariable=t2)    
spin_2.grid(row=7, column=1, padx=5, pady=5,sticky=W)  



label_y1 = ttk.Label(window,width = 20, text = "Min value:")
label_y1.grid(row=8, column=0, padx=5, pady=5)

t3 = tk.IntVar(window,-150)
t4 = tk.IntVar(window,150)

spiny = ttk.Spinbox(window, width = 50, font=('Helvetica', 12),from_= -20000000000, to = 20000000000, textvariable=t3)    
spiny.grid(row=8, column=1, padx=5, pady=5,sticky=W)  


label_y2 = ttk.Label(window,width = 20, text = "Max value:")
label_y2.grid(row=9, column=0, padx=5, pady=5)

spin_y2 = ttk.Spinbox(window, width = 50, font=('Helvetica', 12), from_= -2000000000000, to = 2000000000000, textvariable=t4)    
spin_y2.grid(row=9, column=1, padx=5, pady=5,sticky=W)  


window.mainloop()