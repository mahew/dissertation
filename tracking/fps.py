# import the necessary packages
import datetime

class FPS:
	def __init__(self):
		self._start = None
		self._end = None
		self._num_frames = 0
		self._total_seconds = 0

	def start(self):
		# start the timer
		self._start = datetime.datetime.now()
		return self
	
	def pause(self):    
		# total seconds upto this point
		now = datetime.datetime.now()
		self._total_seconds += (now - self._start).total_seconds()

	def resume(self):
		self._start = datetime.datetime.now()

	def stop(self):
		# stop the timer
		self._end = datetime.datetime.now()

	def update(self):
		# increment the total number of frames examined during the
		# start and end intervals
		self._num_frames += 1

	def elapsed(self):
		# return the total number of seconds between the start and
		# end interval
		return (self._total_seconds + (self._end - self._start).total_seconds())

	def fps(self):
		# compute the (approximate) frames per second
		return self._num_frames / self.elapsed()