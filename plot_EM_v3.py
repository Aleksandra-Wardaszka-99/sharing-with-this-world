import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from PyQt5.QtWidgets import QComboBox, QMainWindow, QApplication, QWidget, QVBoxLayout,QPushButton, QLabel, QSpinBox,QHBoxLayout,QStackedLayout
from PyQt5 import QtCore
import sys
import glob
from tkinter import filedialog
from pathlib import Path
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import math
import mplcursors
from matplotlib.backends.backend_qt5agg import FigureCanvas,NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import os

# Autor: A. Wardaszka
# Opis: Program z interferjsem graficznym. Użytkownik wybiera po naciśnieciu przycisku "Chose path" ścieżkę do pobrania plików .csv 
# ścieżka może być wielokrotnie zmieniana podczas wizualizacji danych na wykresie bez kasowania poprzednich, parametry przedstawiane są 
# z listy "Chose type of chart" która jest stała. Wybrana nazwa pliku z "Chose path" określa, na których danych przeprowadzane są działania
# "Show chart" wyświetla okno z wykresem - wyłączona jest funkcja jego zamknięcia /// polecane jest w przyszłości adjustacja wielkości okna 
# "Add chosen parameter" dodaje określony parametr danych do wykresu, a "Clear plot" kasuje wszystkie zapisane wykresy z subplots pozwalając na 
# rozpoczęcie procesu od nowa. Dane dla danego pliku mogą być niezależnie zapisane w formacie .xlsx. Parametry początkowe i końcowe dla osi wykresu 
# mogą być ustawianie poprzez wpisane wartości całkowitej w "Min freq" "Max freq" "Min value" "Max value". Zamknięcie programu następuje bo 
# wciśnieciu przycisku "Exit"
# pierwsza skończona wersja: 01.10.2025



class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
 

        self.label = QLabel("Choose type of chart :")
        self.label.setFixedSize(QtCore.QSize(130, 30))
        # label.move(100,100)
        

        self.combobox1 = QComboBox()
        self.combobox1.setFixedSize(QtCore.QSize(140, 30))
        self.combobox1.addItems(['RL','SE',
                            'coefficient_transmission',
                            'coefficient_reflection',
                            'Conductivity',
                            'tangens_E',
                            'tangens_M',
                            'E`',
                            'E``',
                            'M`',
                            'M``'])

      

        self.path_way = QLabel("")
       
        self.data = QComboBox()
        self.data.setFixedSize(QtCore.QSize(350, 30))
        self.csv_list = QComboBox()
       
        self.charts_name = []
        
        self.fig ,self.ax_chart = plt.subplots()
        
        self.ax_chart.grid()
       
        win = plt.gcf().canvas.manager.window
        win.setWindowFlags(win.windowFlags() | QtCore.Qt.CustomizeWindowHint)
        win.setWindowFlags(win.windowFlags() & ~QtCore.Qt.WindowCloseButtonHint)
        self.fig.show()
        
        self.button_path = QPushButton('Chose path')
        self.button_path.clicked.connect(lambda: self.path())
        self.button_path.setFixedSize(QtCore.QSize(150, 30))

        openButton = QPushButton("Open Sub Window",  self)
        openButton.clicked.connect(self.openSub)


        self.button_all = QPushButton('Show chart')
        self.button_all.clicked.connect(lambda: self._update_canvas(self.charts_name))
        self.button_all.setFixedSize(QtCore.QSize(150, 30))

        self.button_add = QPushButton('Add')
        self.button_add.clicked.connect(lambda: self.add_plot(self.ax_chart, self.charts_name))
        self.button_add.setFixedSize(QtCore.QSize(150, 30))

        self.button_clear = QPushButton('Clear plot')
        self.button_clear.clicked.connect(lambda: self.clear_plot(self.ax_chart,self.charts_name))
        self.button_clear.setFixedSize(QtCore.QSize(150, 30))

        self.button_exit = QPushButton('Exit')
        self.button_exit.clicked.connect(lambda: self.exit())
        self.button_exit.setFixedSize(QtCore.QSize(150, 30))
        self.labelmin = QLabel("Min value:")
        self.labelmin.setFixedSize(QtCore.QSize(100, 30))
        self.spin3 = QSpinBox()
        self.spin3.setFixedSize(QtCore.QSize(100, 30))
        self.spin3.setValue(-10)
        self.spin3.setMaximum(2147483647)
        self.spin3.setMinimum(-2147483647)
        self.labelmax = QLabel("Max value:")
        self.labelmax.setFixedSize(QtCore.QSize(100, 30))
        self.spin4 = QSpinBox()
        self.spin4.setFixedSize(QtCore.QSize(100, 30))
        self.spin4.setValue(10)
        self.spin4.setMinimum(-2147483647)
        self.spin4.setMaximum(2147483647)
     
        
        layout = QVBoxLayout()
        layout2 = QHBoxLayout()
        layout3 = QHBoxLayout()
        layout4 = QHBoxLayout()
        layout5 = QHBoxLayout()
        layout6 = QHBoxLayout()
        layout2.addWidget(self.label)
        layout2.addWidget(self.combobox1) 
        layout2.addWidget(self.data)
        layout3.addWidget(self.button_path)
        layout3.addWidget(self.button_add)
        layout3.addWidget(self.button_all)
        layout3.addWidget(self.button_clear)
        layout4.addWidget(self.labelmin)
        layout4.addWidget(self.spin3)
        layout4.addWidget(self.labelmax)
        layout4.addWidget(self.spin4)
        layout4.addWidget(self.button_exit)
        
        #layout5.addWidget(self.fig)
        layout2.addWidget(openButton)
       # self.addToolBar(QtCore.Qt.BottomToolBarArea,
       #                 NavigationToolbar(self.canvas, self))
        layout.addLayout(layout2)
        layout.addLayout(layout3)
        layout.addLayout(layout4)
        layout.addLayout(layout5)
        layout.addLayout(layout6)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowCloseButtonHint)
        

        
    def _update_canvas(self,charts_name):
        
        freq_min = 100000000 # self.spin.value()
        freq_max = 18000000000 # self.spin2.value()
        freq_min = int(freq_min)
        freq_max = int(freq_max)
        val_min = self.spin3.value()
        val_max = self.spin4.value()
        val_min = int(val_min)
        val_max = int(val_max)
        self.ax_chart.set_xlim([freq_min, freq_max])
        self.ax_chart.set_ylim([val_min, val_max])
        self.ax_chart.legend(self.charts_name)
        cursor = mplcursors.cursor(self.ax_chart, hover=False)
        cursor.connect('add', self.cursor1_annotations)

        #self.fig.add_axes(self.ax_chart)
        self.fig.canvas.draw_idle()
        #self.ax_chart.figure.canvas.draw()
        
        #self.ax.chart.clear()

    def readfile_csv(self,file,freq,E,Eloss,M,Mloss,Ecomplex,Mcomplex):

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

    def calculate_SE(self,freq,E,Eloss,M,Mloss, SE,Mcomplex,Cond_AC):

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

    def calculate_RL(self,freq,E,Eloss,M,Mloss,RL,coefficient_reflection,input_impedance,Ecomplex,Mcomplex,coefficient_transmission):
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
    

    def calculate_loss_tangens(self,freq,E,Eloss,M,Mloss,tangens_M,tangens_E):
        for i in range(len(E)):
            tangens_E.append((Eloss[i] / E[i]))
            tangens_M.append((Mloss[i] / M[i]))
        tangens_E = np.array(tangens_E)
        tangens_M = np.array(tangens_M)


    def cursor1_annotations(self,sel):
        sel.annotation.set_text(
            'Cursor One:\n x {:.2f} \n y {:.2f} '.format(sel.target[0], sel.target[1]))
        sel.annotation.get_bbox_patch().set(fc="powderblue", alpha=0.9)
    

                
    def add_plot(self,ax_chart,charts_name):
        
        EM_parameter  = self.combobox1.currentText()
        file  = (self.csv_list.currentText()+"/"+self.data.currentText()+".csv")  
        print(file) 
        
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
        self.readfile_csv(file, freq,E,Eloss,M,Mloss,Ecomplex,Mcomplex)
        self.calculate_RL(freq,E,Eloss,M,Mloss,RL,coefficient_reflection,input_impedance,Ecomplex,Mcomplex,coefficient_transmission)
        self.calculate_SE(freq,E,Eloss,M,Mloss, SE,Mcomplex,Cond_AC)
        self.calculate_loss_tangens(freq,E,Eloss,M,Mloss,tangens_M,tangens_E)

        if EM_parameter == "RL":
            self.ax_chart.plot(freq, RL)
            D_name = (data_name_1+"_RL")
            self.ax_chart.set(xlabel='Frequency [Hz]', ylabel='RL [dB]')
            self.charts_name.append(D_name)
            print(D_name)

        if EM_parameter == "SE":
            self.ax_chart.plot(freq, SE)
            D_name = (data_name_1+"_SE")
            self.ax_chart.set(xlabel='Frequency [Hz]', ylabel='SE [dB]')
            self.charts_name.append(D_name)
            print(D_name)

        if EM_parameter == "coefficient_transmission":
            self.ax_chart.plot(freq, coefficient_transmission)
            D_name = (data_name_1+"_coefficient_transmission")
            self.ax_chart.set(xlabel='Frequency [Hz]', ylabel='coefficient_transmission')
            self.charts_name.append(D_name)
            print(D_name)

        if EM_parameter == "Conductivity":
            
            self.ax_chart.plot(freq, Cond_AC)
            D_name = (data_name_1+"_Conductivity")
            self.ax_chart.set(xlabel='Frequency [Hz]', ylabel='Conductivity')
            self.charts_name.append(D_name)
            print(D_name)

        if EM_parameter == "tangens_M":
            
            self.ax_chart.plot(freq, tangens_M)
            D_name = (data_name_1+"_tangens_M")
            self.ax_chart.set(xlabel='Frequency [Hz]', ylabel='tangens_M')
            self.charts_name.append(D_name)
            print(D_name)

        if EM_parameter == "tangens_E":
            
            self.ax_chart.plot(freq, tangens_E)
            D_name = (data_name_1+"_tangens_E")
            self.ax_chart.set(xlabel='Frequency [Hz]', ylabel='tangens_E')
            self.charts_name.append(D_name)
            print(D_name)

        if EM_parameter == "E`":
            self.ax_chart.plot(freq, E)
            D_name = (data_name_1+"_E`")
            self.ax_chart.set(xlabel='Frequency [Hz]', ylabel='Permittivity_real')
            self.charts_name.append(D_name)
            print(D_name)
            
        if EM_parameter == "E``":
            self.ax_chart.plot(freq, Eloss)
            D_name = (data_name_1+"_E``")
            self.ax_chart.set(xlabel='Frequency [Hz]', ylabel='Permittivity_imag')
            self.charts_name.append(D_name)
            print(D_name)

        if EM_parameter == "M`":
            self.ax_chart.plot(freq, M)
            D_name = (data_name_1+"_M`")
            self.ax_chart.set(xlabel='Frequency [Hz]', ylabel='Permeability_real')
            self.charts_name.append(D_name)
            print(D_name)

        if EM_parameter == "M``":
            
            self.ax_chart.plot(freq, Mloss)
            D_name = (data_name_1+"_M``")
            self.ax_chart.set(xlabel='Frequency [Hz]', ylabel='Permeability_imag')
            self.charts_name.append(D_name)
            print(D_name)
        if EM_parameter == "coefficient_reflection":
            
            self.ax_chart.plot(freq, coefficient_reflection)
            D_name = (data_name_1+"_coefficient_reflection")
            self.ax_chart.set(xlabel='Frequency [Hz]', ylabel='coefficient_reflection')
            self.charts_name.append(D_name)
            print(D_name)
            

    def path(self):
        csv_folder = filedialog.askdirectory(initialdir = "C:/<whatever>") 
        self.csv_list.clear()
        path = glob.glob(csv_folder+"/*.csv")   
       
        self.data.clear()
    

        for files in path: 
            
            
            name = Path(files).stem
            basepath = os.path.dirname(os.path.realpath(files))
            #print(name)
            self.csv_list.addItem(basepath)
            #print(basepath)
            self.data.addItem(name)
        
    
        
        
    def exit(self):
        plt.close()
        self.destroy()
        sys.exit()

    def show_plot(self,ax_chart):
        # if plt.figure is False:
        #     fig=plt.figure()
        #     fig.add_axes(ax_chart)
        freq_min = 100000000 # self.spin.value()
        freq_max = 18000000000 # self.spin2.value()
        freq_min = int(freq_min)
        freq_max = int(freq_max)
        val_min = self.spin3.value()
        val_max = self.spin4.value()
        val_min = int(val_min)
        val_max = int(val_max)
        self.ax_chart.set_xlim([freq_min, freq_max])
        self.ax_chart.set_ylim([val_min, val_max])
        self.ax_chart.legend(self.charts_name)
        cursor = mplcursors.cursor(self.ax_chart, hover=False)
        cursor.connect('add', self.cursor1_annotations)
        plt.show()
        # ax.clear()
        # ax = ax_chart
        # if self.canvas is not None:
        #     self.canvas.deleteLater()

        # self.canvas = FigureCanvas(self.fig)

        # self.canvas_layout.addWidget(self.canvas)
       
       
        #self.fig.show()

    def openSub(self):
        self.sub = SubWindow(self.ax_chart)
        self.sub.show()


    def clear_plot(self,ax_chart,charts_name):
        self.ax_chart.clear()
        self.ax_chart.grid()
        self.charts_name.clear()
        print("cleared")

##########################################################
      
class SubWindow(FigureCanvasQTAgg):
    def __init__(self, parent = None):

        fig = Figure(figsize=(8,6))
        self.ax = fig.add_subplot()

       # self.canvas_layout.addWidget(self.canvas)
        super(SubWindow,  self).__init__(self.canvas )
  
    
# class Grid(FigureCanvasQTAgg):
#     def __init__(self, parent = None, width = 5, height = 5, dpi = 120):
#         fig = Figure(figsize=(width, height), dpi=dpi)
#         self.ax = fig.add_subplot()
#         self.ax.set_ylim(-8.75, 8.75)
#         self.ax.set_xlim(-8.75, 8.75)
#         ticks = list(range(-8, 9))
#         self.ax.xaxis.set_ticks(ticks)
#         self.ax.yaxis.set_ticks(ticks)
#         self.ax.grid(visible = True)
#         self.ax.set_axisbelow(True)
#         self.ax.tick_params(axis='both', which='both', length=0, labeltop=True, labelright=True)
#         self.ax.set_aspect('equal')
#         for spine in self.ax.spines.values():
#             spine.set_visible(False)
#         self.title_font_ = {'fontsize': 16, 'fontweight': "normal", 'color': "black", 
#                       'verticalalignment': "center", 'horizontalalignment': "center"}
#         self.ax.set_title("Grid Title", fontdict = self.title_font_, pad = 35)
#         self.circles = []
#         super(Grid, self).__init__(fig)
    
#     def createPattern(self, dots = 8, unified = True):
#         self.dots = dots
#         self.unified = unified
#         # change title
#         self.ax.set_title("Add Pattern", fontdict = self.title_font_, pad = 35)
        
#         x = list(range(-8, -8+dots))
#         y = [8.01]*dots
        
#         if self.unified:
#             coord = np.array(list(map(list, zip(x, y))))
#             for i in range(self.pairs):
#                 circ = self.ax.add_patch(plt.Circle((coord[i,0], coord[i,1]), 0.35, color="royalblue"))
#                 self.circles.append(circ)
#         else:
#             xw = list(range(1, 1+dots))
#             coord_blue = np.array(list(map(list, zip(x, y))))
#             coord_pink = np.array(list(map(list, zip(xw, y))))
#             for i in range(dots):
#                 circ = self.ax.add_patch(plt.Circle((coord_pink[i,0], coord_pink[i,1]), 0.35, color="deeppink"))
#                 self.circles.append(circ)
#             for i in range(dots):
#                 circ = self.ax.add_patch(plt.Circle((coord_blue[i,0], coord_blue[i,1]), 0.35, color="deepskyblue"))
#                 self.circles.append(circ)

 ############################################################       

app = QApplication(sys.argv)
window = MainWindow()
window.show()

sys.exit(app.exec_())
