# To do
# catch keyboard interrupt
# logger on/off via IO
# gopro turn on
# throw away nans
# bluetooth
# log to SD card in fat32 or exfat

#00:19:01:3D:EE:50	XGPS160-3DEE50

import gps, logging, threading, datetime, time
from os import listdir
from time import gmtime, strftime
#================ Global Variables ==================
lognum = 1
avitime = 0

#================GPSD Thread Function==================
class GpsPoller(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    global gpsd #so global value is used
    gpsd = gps.gps(mode=gps.WATCH_ENABLE) #starting the stream of info
    self.current_value = None
    self.running = True #setting the thread running to true
 
  def run(self):
    global gpsd
    lastutc = ""
    while gpsp.running:
      gpsd.next() #this will continue to loop and grab EACH set of gpsd info to clear the buffer
      
      if (gpsd.utc != lastutc) & isinstance(gpsd.utc, basestring): #is there a update and is it a valid reading gpsd.utc is Nonetype until it gets a update
		   log.write_row(gpsd)
		   #print  gpsd.utc,',',gpsd.fix.latitude,',',gpsd.fix.longitude
		   #Call calculations function, how to make sure this call doesnt take too long? how do? perhaps there should be a thread elsewhere that polls UTC for a update and then calls. That way it can be certain that data doesnt stack up or get lost by GPSD
		   #call logging thread function
		   lastutc = gpsd.utc
    print("GPSD is dead")

#=============== Log File Writer ===================

class LogWriter:

	def __init__(self, filename):
                global logbasename
        #open log file
		self.csv_file = open(filename, 'wt',1) #1 = write line at a time
         
        # Write header row
                firstlines = datetime.datetime.now().strftime('File created on %Y-%m-%d @ %H:%M:%S \n \n')
		self.csv_file.write(firstlines)

                self.csv_file.write('[header] \n\
satellites\n\
time\n\
latitude\n\
longitude\n\
velocity kmh\n\
heading\n\
height\n\
avifileindex\n\
avisynctime\n\
\n\
[comments]\n\
rlogger ver 0.0\n\
\n\
[avi]\n\
%s\n\n' % logbasename + #basename for avi file
'[column names]\n\
sats time lat long velocity heading height avifileindex avitime\n\
\n\
[data]\n')
 
	def write_row(self,gpsd):
                global lognum
                global avitime

                satstr = "%03d " % gpsd.satellites_used
                UTCstr = gpsd.utc.split('T')[1].replace(':','').replace('0Z','') + ' '
                latstr = ("%0.5f " % gpsd.fix.latitude).zfill(13)
                longstr = ("%0.5f " % gpsd.fix.longitude).zfill(13)
                velstr = ("%0.3f " % (gpsd.fix.speed * 3.6)).zfill(8)
                headingstr = ("%0.2f " % gpsd.fix.track).zfill(7)
                altitudestr = ("%+.2f " % gpsd.fix.altitude).zfill(10)
                lognumstr = "%04d " % lognum
                avitimestr = "%09d " % avitime
#008 112822.00 003147.80832 -00056.66700 039.551 266.59 +00087.63 0005 000000280 #reference


                data_string = satstr + UTCstr + latstr + longstr + velstr + headingstr + altitudestr + lognumstr + avitimestr
	
		print data_string
                self.csv_file.write(data_string + '\n')
                avitime = avitime + 1 * 1000
	def __del__(self):
		self.csv_file.close()
		print("CSV Log File Closed")
	

#return True

#find next incremental log file name & open log
logdir = '/tmp/'
logbasename = 'log'
logext = '.vbo'

files = listdir(logdir)

filename = logbasename +'1' + logext
while filename in files:
    filename = filename.replace(filename[len(logbasename):-len(logext)],str(int(filename[len(logbasename):-len(logext)]) + 1).zfill(4))
    lognum = lognum + 1
print("Starting Log File: " + logdir + filename)
print lognum
log = LogWriter( logdir + filename) # create log


gpsp = GpsPoller() # create the thread
gpsp.start() # start it up

#print datetime.date.today()
#print datetime.datetime.now()
#print datetime.datetime.now().time()
#print datetime.datetime.now().strftime('%Y-%m-%d @ %H:%M:%S')

#strftime("%Y-%m-%d %H:%M:%S", gmtime())

#print dir(gpsd)
	

