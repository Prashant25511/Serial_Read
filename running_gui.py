# Created in 2020 - Prashant Waiba #
from PyQt5.uic import loadUi
from PyQt5.QtCore import QSize, QRect, QObject, pyqtSignal, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication, QComboBox, QDialog, QMainWindow, QWidget, QLabel, QTextEdit, QListWidget, QListView, QFileDialog
from PyQt5 import QtGui, QtWidgets
import pyqtgraph as pg
from pyqtgraph import  plot
from pyqtgraph.Qt import QtGui, QtCore
import sys 
import serial
import numpy as np
from qt import *
import time
from struct import*
import time
import matplotlib.pyplot as plt
import serial.tools.list_ports

app = QtWidgets.QApplication([])
p = pg.plot()
p.setWindowTitle('LIVE DATA FROM SERIAL PORT')
p.setWindowTitle('LIVE PLOT OF FLUORESCENCE MEASUREMENT')
p.setLabels(bottom = "TIME", left = "ADC_COUNTS_MEAN")
p.resize(800, 700)
curve = p.plot()

##---detect ports and select the port in which STM board is connected----##
	
ports = serial.tools.list_ports.comports()
print("Number of ports connected: ", len(ports))
portName = []
portDesc = []
for port, desc, hwid in sorted(ports):
		# print(port, desc)
	portName.append(port)
	portDesc.append(desc)
	# STLinkString = [s for s in portDesc if "STMicroelectronics STLink Virtual" in s]
	# USBString = [s for s in portDesc if "USB Serial Device" in s]
USBString = [s for s in portDesc if "STMicroelectronics STLink Virtual COM Port" in s]
	# print(STLinkString)
idxMatch = portDesc.index(USBString[0])
comport= portName[idxMatch]

##------------------------------------------------------------##

raw = serial.Serial(comport,baudrate=115200,bytesize=serial.EIGHTBITS,stopbits=serial.STOPBITS_ONE,parity=serial.PARITY_NONE,timeout=100)
# raw.close()
# raw.open()


display_data = np.array([])
chunk_size=10

plt.close("all")
plt.figure()
plt.ion()

class Worker(QObject):

	finished = pyqtSignal()
	current_data_Ready = pyqtSignal(str)
	mean_data_Ready= pyqtSignal(str)
	std_data_Ready= pyqtSignal(str)
	
	@pyqtSlot()
	def __init__(self):
		super(Worker, self).__init__()
		self.working = True
		self.timer = QtCore.QTimer()
		# self.timer.setInterval(0)
		self.timer.timeout.connect(self.work)
		self.timer.start()

	def work(self):
		global  display_data
		current_data = np.zeros(chunk_size)
		
		# while (raw.inWaiting()==0):
		# 	pass
		# raw.flushInput()
		for j in range(10):
			# float(raw.readline().decode().replace('\r', '').replace('\n', ''))
			float(raw.readline().decode("utf-8").rstrip("\r\n"))

	
		# time.time_ns()
		

		
		while self.working:
			
			for i in range(chunk_size):
				# time.time_ns()

				# current_data[i] = float(raw.readline().decode().replace('\r', '').replace('\n', ''))
				current_data[i] = float(raw.readline().decode("utf-8").rstrip("\r\n"))
				
				self.current_data_Ready.emit(str(current_data[i]))
			display_data = np.append(display_data, current_data)
			curve.setData(display_data) #----------draw the graph
				
			mean_data = np.round(np.mean(current_data))
			std_data = np.round(np.std(current_data))
			# coeff_variance = np.divide(std_data, mean_data)
			# # print(coeff_variance)
			 
			self.mean_data_Ready.emit(str(mean_data)) 
			self.std_data_Ready.emit(str(std_data))            #--------print data in edit line
			# display_data = np.append(display_data, current_data)
			# curve.setData(display_data) #----------draw the graph
			
			# plt.plot(display_data, color = "r")
			# plt.pause(0.1)
			
			app.processEvents()

			

		self.finished.emit()

class qt(QMainWindow):
	def __init__(self):
		QMainWindow.__init__(self)
		loadUi('qt.ui', self)
		self.thread = None
		self.worker = None
		self.pushButton.clicked.connect(self.start_loop)
		self.pushButton_6.clicked.connect(self.save_mean_Button)
		self.pushButton_5.clicked.connect(self.save_std_Button)
		self.pushButton_7.clicked.connect(self.save_serial_data_Button)
		self.pushButton_8.clicked.connect(self.clear)
		
	# def loop_finished(self):...
		# print('Looped Finished')

	def start_loop(self):
		self.worker = Worker()  
		self.thread = QThread() 
		self.worker.moveToThread(self.thread)  
		self.thread.started.connect(self.worker.work)
		# self.thread.started.connect(self.worker.work2)
		self.worker.current_data_Ready.connect(self.current_data_display)
		self.worker.mean_data_Ready.connect(self.mean_data_display)
		self.worker.std_data_Ready.connect(self.std_data_display)
		self.pushButton_2.clicked.connect(self.stop_loop) 

		# self.worker.finished.connect(self.loop_finished)  

		# self.worker.finished.connect(self.thread.quit)  
		# self.worker.finished.connect(self.worker.deleteLater)  
		# self.thread.finished.connect(self.thread.deleteLater)  
		# # self.thread.start()   ##forecely stoping the thread
		# raw.flushInput()

	

	def stop_loop(self):
		self.worker.working = False

	def current_data_display(self, string):
		self.textEdit_3.append("{}".format(string))
		self.textEdit_3.verticalScrollBar().setValue(100000000)
		# print(i)        #---i refers data in serial port

	def mean_data_display(self, str):
		self.textEdit_5.append("{}".format(str))
		self.textEdit_5.verticalScrollBar().setValue(100000000)
		
	def std_data_display(self, str):
		self.textEdit_6.append("{}".format(str))
		self.textEdit_6.verticalScrollBar().setValue(100000000)
	
	def on_pushButton_2_clicked(self):
		self.textEdit.setText('Stop and reconnect...')
		self.progressBar.setValue(0)
	def on_pushButton_clicked(self):

		self.completed = 0
		while self.completed < 100:
			self.completed += 0.001
			self.progressBar.setValue(self.completed)
		self.textEdit.setText('Receiving data...')
		self.label_8.setText("Connect")
		self.label_8.setStyleSheet('color: green')
		x = 1
		self.textEdit_3.setText("Serial_Data")
		self.textEdit_5.setText("Mean")
		self.textEdit_6.setText("Standard_Deviation")

	def save_serial_data_Button(self):
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		fileName, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()","","All Files (*);;Text Files (*.txt)", options=options)
		# print(fileName)
		k = open(fileName, 'w')
		my_save_serial_data = self.textEdit_3.toPlainText()
		k.write(my_save_serial_data)

	def save_std_Button(self):
		# file_filter = 'Data File (*.xlsx *.csv *.dat);; Excel File (*.xlsx *.xls)'
		# response = QFileDialog.getSaveFileName(
		# 	parent=self,
		# 	caption='Select a data file',
		# 	directory= 'Data File.dat',
		# 	filter=file_filter,
		# 	initialFilter='Excel File (*.xlsx *.xls)'
		# )
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		fileName, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()","","All Files (*);;Text Files (*.txt)", options=options)
		# print(fileName)
		f = open(fileName, 'w')
		# with open(filename.txt, 'w') as f:
		my_std = self.textEdit_6.toPlainText()
		f.write(my_std)

	def save_mean_Button(self):
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		fileName, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()","","All Files (*);;Text Files (*.txt)", options=options)
		# print(fileName)
		g = open(fileName, 'w')
		my_mean = self.textEdit_5.toPlainText()
		g.write(my_mean)
	
	def clear(self):
		global display_data
		self.worker.working = False
		# log.debug('clean graph')
		current_data = []
		display_data = []
		curve.setData(display_data)
		app.processEvents()
		
	


def main():
	app = QtWidgets.QApplication(sys.argv)
	main = qt()
	main.show()
	sys.exit(app.exec())

if __name__ == '__main__':
	main()
	
	
