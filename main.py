# To do
# catch keyboard interrupt
# logger on/off via IO
# throw away nans


import gps, logging, datetime, time
from threading import Thread
from os import listdir
from time import time
from Queue import Queue



#================ Global Variables ==================
lognum = 1
avitime = 0
logdir = '/tmp/'
logbasename = 'log'
logext = '.vbo'

start_speed_threshold = 45 #km/hr
start_delay = 2 #seconds

stop_speed_threshold = 40 #km/hr
stop_delay = 3 #seconds

queue = Queue(10)

#================GPSD Thread Function==================
class GpsPoller(Thread):
	def __init__(self):
		Thread.__init__(self)
		global gpsd #so global value is used
		lastutc = ""
		gpsd = gps.gps(mode=gps.WATCH_ENABLE) #starting the stream of info
		self.current_value = None
		self.running = True #setting the thread running to true
	def run(self):
		global gpsd
		global queue
		lastutc = ""

#        if tpv.mode >= gps.MODE_2D and hasattr(tpv, "lat") and hasattr(tpv, "lon"):
#gobject.io_add_watch in xgpsspeed is interesting in watch function. maybe replace next with that method
		try:
			while gpsp.running:
				gpsd.next() #pull next set of data from gpsd
				#print(gpsd.fix.MODE_2D)
				#'TPV': Time Position Velocity Report, 'SKY': satellite and accuracy report. 
				if (gpsd.data['class'] == 'TPV') and (gpsd.utc != lastutc) and (gpsd.data.mode >= gps.MODE_2D):		
					#print(gpsd.utc)
					queue.put(gpsd)
					lastutc = gpsd.utc
		except StopIteration:
			print("stop iteration caught, GPSD closed socket")

		print("GPSD is dead")

#=============== GPS Consumer Thread ===================
class GpsConsumer(Thread):	
	def run(self):
		logging = False
		global queue
		global start_speed_threshold
		global stop_speed_threshold
		global speed_time
		global start_delay
		global stop_delay
		timerstart = 0
		timerstop = 0

		while True:
			data = queue.get()
			curtime =time()
			curspeed = (gpsd.fix.speed * 3.6)

			print curtime, (curtime - timerstart), (curtime - timerstop), (gpsd.fix.speed * 3.6)

			if (not logging) and  (curspeed > start_speed_threshold) and (timerstart==0): #start timer
				timerstart = curtime
				print "Start Timer Marked"
			elif (not logging) and  (curspeed <= start_speed_threshold) and (timerstart > 0): #restart time if time dips
				timerstart = 0
				print "Start Timer Restarted"
			elif (not logging) and  (curspeed > start_speed_threshold) and (timerstart!=0) and ((curtime - timerstart) > start_delay): #start a log if timer lapsed
				log = LogWriter(logdir, logbasename) # create log
				logging = True
				timerstart = 0
			elif logging and (curspeed < stop_speed_threshold) and (timerstop == 0): #if speed drops start timing
				timerstop = curtime
				print "Stop Timer Marked"
			elif logging and (curspeed >= stop_speed_threshold) and (timerstop > 0): #if speed recovers stop timing
				timerstop = 0
				print "Stop Timer Restarted"
			elif logging and (curspeed < stop_speed_threshold) and (timerstop!=0) and ((curtime - timerstop) > stop_delay): #stop log after timer lapses
				timerstop = 0
				print "Ending Log"
				logging = False
				log.end_log()



			if logging:
				log.write_row(data)
				#print "Consumed", data.utc , queue.qsize()
			queue.task_done()

#=============== Log File Writer ===================
class LogWriter():
	def __init__(self, logdir, logbasename):
		#find next incremental log file name & open log
		global lognum
		files = listdir(logdir)

		filename = logbasename +'0001' + logext
		while filename in files:
			filename = filename.replace(filename[len(logbasename):-len(logext)],str(int(filename[len(logbasename):-len(logext)]) + 1).zfill(4))
			lognum = lognum + 1
		print("Starting Log File: " + logdir + filename)

	        #open log file
		self.csv_file = open(logdir + filename, 'wt',1) #1 = write line at a time
         
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
	def build_string(self,gpsd):
                global lognum
                global avitime
                satstr = "%03d " % gpsd.satellites_used
                UTCstr = gpsd.utc.split('T')[1].replace(':','').replace('0Z','') + ' '
                latstr = ("%0.5f " % gpsd.fix.latitude).zfill(13)
                longstr = ("%0.5f " % gpsd.fix.longitude).zfill(13)
                velstr = ("%0.3f " % (gpsd.fix.speed * 3.6)).zfill(8) #m/s to km/hr
                headingstr = ("%0.2f " % gpsd.fix.track).zfill(7)
                altitudestr = ("%+.2f " % gpsd.fix.altitude).zfill(10)
                lognumstr = "%04d " % lognum
                avitimestr = "%09d " % avitime

                data_string = satstr + UTCstr + latstr + longstr + velstr + headingstr + altitudestr + lognumstr + avitimestr
		#print(data_string.find('nan'))
		return data_string

	 
	def write_row(self,gpsd):
		global avitime
		data_string = self.build_string(gpsd)
		print(data_string)
                self.csv_file.write(data_string + '\n')
                avitime = avitime + 1 * 1000
	def end_log(self):
		self.csv_file.close()
		print("CSV Log File Closed")

	def __del__(self):
		self.csv_file.close()

	
#=============== Main Function ===================

gpsp = GpsPoller() # create the thread
gpsp.start() # start it up
Consumer = GpsConsumer()
Consumer.start()



#print datetime.date.today()
#print datetime.datetime.now()
#print datetime.datetime.now().time()
#print datetime.datetime.now().strftime('%Y-%m-%d @ %H:%M:%S')

#strftime("%Y-%m-%d %H:%M:%S", gmtime())

#print dir(gpsd)
	

