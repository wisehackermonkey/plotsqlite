#Introduction

This application can be used to to create time series and xy plots from data stored in a sqlite database.

The application may be downloaded from here. Then unzip the whole folder close to root (i.e. not in 'Program Files..') and launch plotsqlite.exe.

* To create time series plots, tables in the database must have one column with date and time on format 'yyyy-mm-dd hh:mm:ss' (or truncated) to be plotted on x-axis and a numeric column to be plotted on y-axis. Additional columns may be used for filtering and/or other plots.
* To create xy scatter plots, tables in the database just needs two numerical columns.
* The project is also closely related to the Midvatten plugin for qgis. 

#PlotSQLite basics

PlotSQLite is an application for creating 2D-plots (primarily time series but also xy scatter) from data stored in a sqlite databse. The application is closely related to Midvatten plugin för QGIS and is meant to be a supplement with better layout options including headers, scaling legend position etc. See screen dump:

The application is early alpha stage but still useful. Download [latest zip file from here] (https://drive.google.com/folderview?id=0B1vhrFUx2OZBVUpFRm92bFZ5R2c&usp=sharing), unzip whole folder close to root (i.e. not in 'Program Files..') and launch plotsqlite.exe. Please maximize the window for best resolution.

Note, earlier I made single-file executables but due to a bug in PyInstaller? this is not possible at the moment. I will revert to this as soon as the bug is fixed.

If you are upgrading from an earlier version of plotsqlite, delete ALL old files and replace with the content in latest zip.
#Usage
##Left part of the main window

A. Select database and then, to enable simultaneous plot from up to three different tables, set the following in tabs 1-3:

B. Select table and columns for x- and y-axis.

C. If using a Midvatten db (from Midvatten plugin for QGIS or perhaps sample data from this site) then select obsid as filtre#1 and then select the objects of interest.

D. Select plot type, e.g. "line and marker"

E. Press "Plot Chart"
##Right part of the main window

The following may be changed several times after clicking "plot chart".

A. Set title and axis titles

B. Set min and max for axis. If these fields are left as defaults then the application will autoscale the axes (ordinary pan- and zoom tools usable independently of this choice). Note that setting Xmin and Xmax is so far only possible for time series plots.

C. Legend xpos and ypos is a relative position (0-1) along axis and set position for the legend (if legend check box is activated). The legend may also be moved manually afterwards by point-and-click with the mouse.

D. Check the box for grid lines if wanted and finally press "Redraw"
#Remember

The application will remember last selections in the left pane. This may cause performance issues if a table with big amounts of data is selected in any hidden tab and the user selects "Plot Chart" without checking all tabs first. -> Always check all tabs before pressing "Plot Chart"! 

_Copyright (c) 2014 Josef Källgården_
