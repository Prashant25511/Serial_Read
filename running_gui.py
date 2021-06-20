from PyQt5.uic import loadUi
from PyQt5.QtCore import QSize, QRect, QObject, pyqtSignal, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication, QComboBox, QDialog, QMainWindow, QWidget, QLabel, QTextEdit, QListWidget, QListView, QFileDialog
from PyQt5 import QtGui, QtWidgets
import pyqtgraph as pg
from pyqtgraph import PlotWidget, plot
from pyqtgraph.Qt import QtGui, QtCore
import sys 
import serial
import numpy as np
from main import *

app = QtGui.QApplication([])

p = pg.plot()
p.setWindowTitle('live plot from serial')

curve = p.plot()



raw=serial.Serial("com6",baudrate=115200,bytesize=8,stopbits=1,timeout=1)

display_data = []
chunk_size=50

#------work thread begins for serial read and plot--------#

class Worker(QObject):
	finished = pyqtSignal()
	intReady = pyqtSignal(str)


	@pyqtSlot()
	def __init__(self):
		super(Worker, self).__init__()
		self.working = True

		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.work)
		self.timer.start()

	def work(self):
		global  display_data
		current_data = np.zeros(chunk_size, dtype = 'int16')      #**-----issue with dtype as values overvalue(need to be figured out)--OverflowError: Python int too large to convert to C long
		
		while self.working:
			while (raw.inWaiting()==0):
				pass


			for j in range(chunk_size):
				current_data[j]=raw.readline()
			
			# try:
			# 	mean_data=np.mean(current_data[-2:])             #--------forcefully deleted the two first readings(why overloading happens in serialport neeeds to find out)
			# 	self.intReady.emit(str(mean_data))               #--------print data in edit line
			# 	display_data = np.append(display_data, mean_data)
			# 	curve.setData(display_data)                      #--------draw the graph
			# 	app.processEvents()	                             #----------update the graph

			# except OverflowError as of:	                        
								
			# 	...

		   
			mean_data=np.mean(current_data[-2:])             #--------forcefully deleted the two first readings(why overloading happens in serialport neeeds to find out)
			self.intReady.emit(str(mean_data))               #--------print data in edit line
			display_data = np.append(display_data, mean_data)
			curve.setData(display_data)                      #--------draw the graph
			app.processEvents()	                             #----------update the graph

			# except OverflowError as of:	                        
								
			# 	...



		self.finished.emit()

class qt(QMainWindow):

	def __init__(self):

		QMainWindow.__init__(self)
		loadUi('qt.ui', self)
		self.thread = None
		self.worker = None
		self.pushButton.clicked.connect(self.start_loop)
		self.pushButton_5.clicked.connect(self.onpushButton)


	def loop_finished(self):
		print('Looped Finished')

	def start_loop(self):

		self.worker = Worker()  
		self.thread = QThread() 
		self.worker.moveToThread(self.thread)  
		self.thread.started.connect(self.worker.work)
		self.worker.intReady.connect(self.onIntReady)
		self.pushButton_2.clicked.connect(self.stop_loop) 
		self.worker.finished.connect(self.loop_finished)  
		self.worker.finished.connect(self.thread.quit)  
		self.worker.finished.connect(self.worker.deleteLater)  
		self.thread.finished.connect(self.thread.deleteLater)  
	
		self.thread.start() 


	def stop_loop(self):
		self.worker.working = False

	# def onIntReady(self, i):
	# 	self.textEdit_3.append("{}".format(i))
	# 	# print(i)        #---i refers data in serial port




	def onIntReady(self, i):
		self.textEdit_3.append("{}".format(i))
		self.textEdit_3.verticalScrollBar().setValue(1000000)
		# self.textEdit_3.verticalScrollBar().setValue(Maximum())


	
	
		



			



	def on_pushButton_2_clicked(self):      #--------disconnect-------------------#
		self.textEdit.setText('Stop and reconnect...')


	def on_pushButton_clicked(self):         #-------PROGRESS BAR COONECTION---------#

		self.completed = 0
		while self.completed < 100:
			self.completed += 0.001
			self.progressBar.setValue(self.completed)
		self.textEdit.setText('Receiving data...')
		self.label_5.setText("Connect")
		self.label_5.setStyleSheet('color: green')
		x = 1
		self.textEdit_3.setText("DATA_START")



	def onpushButton(self):
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		fileName, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()","","All Files (*);;Text Files (*.txt)", options=options)
		print(fileName)
		f = open(fileName, 'w')

		
		# with open(filename.txt, 'w') as f:
		my_text = self.textEdit_3.toPlainText()
		f.write(my_text)





if __name__ == '__main__':
	app = QtWidgets.QApplication(sys.argv)
	main = qt()
	main.show()
	sys.exit(app.exec())


	
	
	
	# file_filter = 'Data File (*.xlsx *.csv *.dat);; Excel File (*.xlsx *.xls)'
		# response = QFileDialog.getSaveFileName(
		# 	parent=self,
		# 	caption='Select a data file',
		# 	directory= 'Data File.dat',
		# 	filter=file_filter,
		# 	initialFilter='Excel File (*.xlsx *.xls)'
		# )
		# print(response)
		