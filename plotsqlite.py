# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : PlotSQLite
Description          : Plots charts from data stored in a SQLite database
Date                 : 2012-12-03 
Author               : Josef Källgården
email                : groundwatergis@gmail.com 
 ***************************************************************************/
"""
# Import the sys, os, locale and PyQt libraries
import sys, os, locale
from PyQt4 import QtGui, QtCore, uic#, QtSql
from functools import partial # only to get combobox signals to work

# 
from sqlite3 import dbapi2 as sqlite
import numpy as np
import matplotlib.pyplot as plt   
from matplotlib.dates import datestr2num
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
import datetime
import matplotlib.ticker as tick
from HtmlDialog import HtmlDialog
from PlotSQLite_MainWindow import Ui_MainWindow

class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self, parent = None):
        #QtGui.QMainWindow.__init__(self, parent)#the line below is for some reason preferred
        super(MainWindow, self).__init__(parent)#for some reason this is supposed to be better than line above
        #QDialog.__init__( self ) #if not working with an application with mainwindow
        #self.iface = iface

        #self=Ui_MainWindow()#new
                
        self.setupUi( self )#due to initialisation of Ui_MainWindow instance
        self.initUI()

        self.database = ''
        self.table = ''
        #self.database_pyqt4provider = QtSql.QSqlDatabase.addDatabase("QSQLITE","db1")
        
    def initUI(self):
        self.table_ComboBox.clear()  
        self.clearthings()
        self.quit_Qaction.triggered.connect(self.quit_app)
        self.actionAbout.triggered.connect(self.about)          
        self.selectDB_QAction.triggered.connect(self.selectFile)          
        self.selectDB_QPushButton.clicked.connect(self.selectFile)          
        # whenever Time Series Table is changed, the column-combobox must be updated and TableCheck must be performed (function partial due to problems with currentindexChanged and Combobox)
        self.connect(self.table_ComboBox, QtCore.SIGNAL("currentIndexChanged(int)"), partial(self.TableChanged)) 
        self.connect(self.Filter1_ComboBox, QtCore.SIGNAL("currentIndexChanged(int)"), partial(self.Filter1Changed)) 
        self.connect(self.Filter2_ComboBox, QtCore.SIGNAL("currentIndexChanged(int)"), partial(self.Filter2Changed)) 
        self.PlotChart_QPushButton.clicked.connect(self.drawPlot)
        self.Redraw_pushButton.clicked.connect( self.refreshPlot )
        
        # Create a plot window with one single subplot
        self.figure = plt.figure() 
        self.axes = self.figure.add_subplot( 111 )
        self.canvas = FigureCanvas( self.figure )
        self.mpltoolbar = NavigationToolbar( self.canvas, self.widgetPlot )
        lstActions = self.mpltoolbar.actions()
        self.mpltoolbar.removeAction( lstActions[ 7 ] )
        self.layoutplot.addWidget( self.canvas )
        self.layoutplot.addWidget( self.mpltoolbar )

        self.show()
        
    def quit_app(self):
        self.close()
        #QtSql.QSqlDatabase.removeDatabase("db1")
        QtCore.QCoreApplication.instance().quit()

    def drawPlot(self):  
        self.axes.clear()
        conn = sqlite.connect(str(self.selected_database_QLineEdit.text()).encode('latin-1'),detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
        # skapa en cursor
        curs = conn.cursor()
        # Valda filter
        filter1 = str(self.Filter1_ComboBox.currentText())
        filter1list = self.Filter1_QListWidget.selectedItems()
        filter2 = str(self.Filter2_ComboBox.currentText())
        filter2list= self.Filter2_QListWidget.selectedItems()
        self.p=[None]*max(len(filter1list),1)*max(len(filter2list),1) # List for plot objects
        self.plabels=[None]*max(len(filter1list),1)*max(len(filter2list),1) # List for plot labels
        #self.plabels = {}

        My_format = [('date_time', datetime.datetime), ('values', float)] #Define (with help from function datetime) a good format for numpy array 
        i = 0
        while i < len(self.p):
            if not (filter1 == '' or filter1==' ') and not (filter2== '' or filter2==' '):
                for item1 in filter1list:
                    for item2 in filter2list:
                        sql = r""" select """ + str(self.xcol_ComboBox.currentText()) + """, """ + str(self.ycol_ComboBox.currentText()) + """ from """ + str(self.table_ComboBox.currentText()) + """ where """ + filter1 + """='""" + str(item1.text())+ """' and """ + filter2 + """='""" + str(item2.text())+ """' order by """ + str(self.xcol_ComboBox.currentText())
                        self.plabels[i] = str(item1.text()) + """, """ + str(item2.text())
                        self.createsingleplotobject(sql,i,My_format,curs)
                        i += 1
            elif not (filter1 == '' or filter1==' '):
                for item1 in filter1list:
                    sql = r""" select """ + str(self.xcol_ComboBox.currentText()) + """, """ + str(self.ycol_ComboBox.currentText()) + """ from """ + str(self.table_ComboBox.currentText()) + """ where """ + filter1 + """='""" + str(item1.text())+ """' order by """ + str(self.xcol_ComboBox.currentText())
                    self.plabels[i] = str(item1.text()) 
                    self.createsingleplotobject(sql,i,My_format,curs)
                    i += 1
            elif not (filter2 == '' or filter2==' '):
                for item2 in filter2list:
                    sql = r""" select """ + str(self.xcol_ComboBox.currentText()) + """, """ + str(self.ycol_ComboBox.currentText()) + """ from """ + str(self.table_ComboBox.currentText()) + """ where """ + filter2 + """='""" + str(item2.text())+ """' order by """ + str(self.xcol_ComboBox.currentText())
                    self.plabels[i] = str(item2.text())
                    self.createsingleplotobject(sql,i,My_format,curs)
                    i += 1            
            else:
                sql = r""" select """ + str(self.xcol_ComboBox.currentText()) + """, """ + str(self.ycol_ComboBox.currentText()) + """ from """ + str(self.table_ComboBox.currentText()) + """ order by """ + str(self.xcol_ComboBox.currentText())
                self.plabels[i] = str(self.ycol_ComboBox.currentText())+""", """+str(self.table_ComboBox.currentText())
                self.createsingleplotobject(sql,i,My_format,curs)
                i += 1
        #rs.close() # close the cursor
        conn.close()  # close the database
        self.refreshPlot()

    def createsingleplotobject(self,sql,i,My_format,curs):
        rs = curs.execute(sql) #Send SQL-syntax to cursor
        recs = rs.fetchall()  # All data are stored in recs
        #Transform data to a numpy.recarray
        table = np.array(recs, dtype=My_format)  #NDARRAY
        table2=table.view(np.recarray)   # RECARRAY transform the 2 cols into callable objects
        myTimestring = []  #LIST
        j = 0
        for row in table2:
            myTimestring.append(table2.date_time[j])
            j = j + 1
        numtime=datestr2num(myTimestring)  #conv list of strings to numpy.ndarray of floats
        if self.PlotType_comboBox.currentText() == "marker":
                self.p[i], = self.axes.plot_date(numtime, table2.values,  'o',label=self.plabels[i])  
        elif self.PlotType_comboBox.currentText()  == "line":
                self.p[i], = self.axes.plot_date(numtime, table2.values,  '-',label=self.plabels[i])  
        elif self.PlotType_comboBox.currentText()  == "line and cross":
                self.p[i], = self.axes.plot_date(numtime, table2.values,  '+-', markersize = 6,label=self.plabels[i])  
        elif self.PlotType_comboBox.currentText()  == "line and marker":
                self.p[i], = self.axes.plot_date(numtime, table2.values,  'o-',label=self.plabels[i])  
        elif self.PlotType_comboBox.currentText()  == "step-pre":
                self.p[i], = self.axes.plot_date(numtime, table2.values, drawstyle='steps-pre', linestyle='-', marker='None',label=self.plabels[i]) # 'steps-pre' best for precipitation and flowmeters, optional types are 'steps', 'steps-mid', 'steps-post'  
        elif self.PlotType_comboBox.currentText()  == "step-post":
                self.p[i], = self.axes.plot_date(numtime, table2.values, drawstyle='steps-post', linestyle='-', marker='None',label=self.plabels[i]) # 'steps-pre' best for precipitation and flowmeters, optional types are 'steps', 'steps-mid', 'steps-post'  
        else:   #LINES WITH DOTS IS DEFAULT
                self.p[i], = self.axes.plot_date(numtime, table2.values,  'o-',label=self.plabels[i])
                
    def refreshPlot( self ):
        self.axes.legend_=None
        #self.axes.clear()
        #self.plabels = ('Rb1103','Rb1104')#debugging
        #print self.plabels #debug
        datemin = self.spnMinX.dateTime().toPyDateTime()
        datemax = self.spnMaxX.dateTime().toPyDateTime()
        if datemin == datemax: #xaxis-limits
            pass
        else:
            self.axes.set_xlim(min(datemin, datemax),max(datemin, datemax))            
        if self.spnMinY.value() == self.spnMaxY.value(): #yaxis-limits
            pass
        else:
            self.axes.set_ylim(min(self.spnMaxY.value(), self.spnMinY.value()),max(self.spnMaxY.value(), self.spnMinY.value()))            
        self.axes.yaxis.set_major_formatter(tick.ScalarFormatter(useOffset=False, useMathText=False))#yaxis-format
        self.figure.autofmt_xdate()#xaxis-format
        self.axes.grid(self.Grid_checkBox.isChecked() )#grid
        if not self.title_QLineEdit.text()=='':#title
            self.axes.set_title(self.title_QLineEdit.text())
        if not self.xtitle_QLineEdit.text()=='':#xaxis label
            self.axes.set_xlabel(self.xtitle_QLineEdit.text())
        if not self.ytitle_QLineEdit.text()=='':#yaxis label
            self.axes.set_ylabel(self.ytitle_QLineEdit.text())
        for label in self.axes.xaxis.get_ticklabels():
            label.set_fontsize(10)
        for label in self.axes.yaxis.get_ticklabels():
            label.set_fontsize(10)
        # finally, the legend
        if self.Legend_checkBox.isChecked():
            if (self.spnLegX.value() ==0 ) and (self.spnLegY.value() ==0):
                leg = self.axes.legend(self.p, self.plabels)
            else:
                leg = self.axes.legend(self.p, self.plabels, bbox_to_anchor=(self.spnLegX.value(),self.spnLegY.value()),loc=10)
            leg.draggable(state=True)
            frame  = leg.get_frame()    # the matplotlib.patches.Rectangle instance surrounding the legend
            frame.set_facecolor('1')    # set the frame face color to white                
            frame.set_fill(False)    # set the frame face color to white                
            for t in leg.get_texts():
                t.set_fontsize(10)    # the legend text fontsize
        else:
            self.axes.legend_=None

        self.figure.autofmt_xdate()
        self.canvas.draw()

    def selectFile(self):   #Open a dialog to locate the sqlite file and some more...
        path = QtGui.QFileDialog.getOpenFileName(None,QtCore.QString.fromLocal8Bit("Select database:"),"*.sqlite")
        if path: 
            self.database = path # To make possible cancel the FileDialog and continue loading a predefined db
        self.openDBFile()

    def openDBFile( self ):    # Open the SpatiaLite file to extract info about tables 
        if os.path.isfile( unicode( self.database ) ):
            self.selected_database_QLineEdit.setText(self.database)
            self.table_ComboBox.clear()  
            self.clearthings()
            conn = sqlite.connect( str(self.database) )
            
            cursor = conn.cursor()
            rs=cursor.execute(r"""SELECT tbl_name FROM sqlite_master WHERE (type='table' or type='view') and not (name = 'geom_cols_ref_sys' or name = 'geometry_columns' or name = 'geometry_columns_auth' or name = 'spatial_ref_sys' or name = 'spatialite_history' or name = 'sqlite_sequence' or name = 'sqlite_stat1' or name = 'views_geometry_columns' or name = 'virts_geometry_columns') ORDER BY tbl_name""" )  #SQL statement to get the relevant tables in the spatialite database
            #self.dbTables = {} 
            self.table_ComboBox.addItem('')
    
            for row in cursor:
                self.table_ComboBox.addItem(row[0])
            
            rs.close()
            conn.close()        

    def clearthings(self):   #Open a dialog to locate the sqlite file and some more...
        self.xcol_ComboBox.clear()
        self.ycol_ComboBox.clear()
        self.Filter1_ComboBox.clear() 
        self.Filter2_ComboBox.clear() 
        self.Filter1_QListWidget.clear()
        self.Filter2_QListWidget.clear()

    def TableChanged(self):     #This method is called whenever table is changed
        # First, update combobox with columns
        self.clearthings()
        self.table = str(self.table_ComboBox.currentText())
        self.PopulateComboBox('xcol_ComboBox', self.table_ComboBox.currentText())  # GeneralNote: For some reason it is not possible to send currentText with the SIGNAL-trigger
        self.PopulateComboBox('ycol_ComboBox', self.table_ComboBox.currentText())  # See GeneralNote
        self.PopulateComboBox('Filter1_ComboBox', self.table_ComboBox.currentText())  # See GeneralNote
        self.PopulateComboBox('Filter2_ComboBox', self.table_ComboBox.currentText())  # See GeneralNote

    def PopulateComboBox(self, comboboxname='', table=None):
        #print str(getattr(self, comboboxname))    # debug
        """This method fills comboboxes with columns for selected tool and table"""
        columns = self.LoadColumnsFromTable(table)    # Load all columns into a list 'columns'
        if len(columns)>0:    # Transfer information from list 'columns' to the combobox
            getattr(self, comboboxname).addItem('')
            for columnName in columns:
                getattr(self, comboboxname).addItem(columnName)  # getattr is to combine a function and a string to a combined function
        
    def LoadColumnsFromTable(self, table=''):
        """ This method returns a list with all the columns in the table"""
        if len(table)>0 and len(self.database)>0:            # Should not be needed since the function never should be called without existing table...
            #QMessageBox.information(None, "info", "now going for columns in table "+  str(table))    # DEBUGGING
            conn = sqlite.connect(str(self.database))  
            curs = conn.cursor()
            #sql = r"""PRAGMA table_info('"""  + str(self.Table) + """')""" #Did not really work as expected
            sql = r"""SELECT * FROM '"""
            sql += str(table)
            sql += """'"""     
            sql2 = str(sql).encode(locale.getdefaultlocale()[1])  #To get back to uniciode-string
            rs = curs.execute(sql2)  #Send the SQL statement to get the columns in the table            
            columns = {} 
            columns = [tuple[0] for tuple in curs.description]
            rs.close()
            conn.close()
        else:
            #QMessageBox.information(None,"info","no table is loaded")    # DEBUGGING
            columns = {}
        return columns        # This method returns a list with all the columns in the table

    def Filter1Changed(self):
        # First, update combobox with columns
        if not self.Filter1_ComboBox.currentText()=='':
            self.Filter1_QListWidget.clear()
            self.PopulateFilterList('Filter1_QListWidget', self.Filter1_ComboBox.currentText())  # For some reason it is not possible to send currentText with the SIGNAL-trigger
        
    def Filter2Changed(self):
        # First, update combobox with columns
        if not self.Filter2_ComboBox.currentText()=='':
            self.Filter2_QListWidget.clear()
            self.PopulateFilterList('Filter2_QListWidget', self.Filter2_ComboBox.currentText())  # For some reason it is not possible to send currentText with the SIGNAL-trigger

    def PopulateFilterList(self, QListWidgetname='', filtercolumn=None):
        sql = "select distinct " + str(filtercolumn) + " from " + self.table
        list_data=sql_load_fr_db(self.database, sql)
        for post in list_data:
            item = QtGui.QListWidgetItem(str(post[0]).encode(locale.getdefaultlocale()[1]))  #.encode due to terrible encoding issues in the db!!!!
            getattr(self, QListWidgetname).addItem(item)

    def about(self):   
        filenamepath = os.path.join(os.sep,os.path.dirname(os.path.abspath(__file__)),"about.htm")
        #print os.path.dirname(os.path.abspath(__file__)) debugging
        dlg = HtmlDialog("About PlotSQLite - Midvatten plot generator for reports",QtCore.QUrl.fromLocalFile(filenamepath))
        dlg.exec_()
        #QtGui.QMessageBox.information(None, "info", filenamepath)    # debugging
        
                
def sql_load_fr_db(dbpath, sql=''):
    conn = sqlite.connect(str(dbpath),detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
    curs = conn.cursor()
    sql2 = str(sql).encode('utf-8') 
    resultfromsql = curs.execute(sql2) #Send SQL-syntax to cursor
    result = resultfromsql.fetchall()
    resultfromsql.close()
    conn.close()
    return result
     
def main():
    app=QtGui.QApplication.instance() # checks if QApplication already exists 
    if not app: # create QApplication if it doesnt exist 
        app = QtGui.QApplication(sys.argv)     
        MainWindow()
    sys.exit(app.exec_())#comment out when using Ipython

if __name__ == "__main__":
    main()
