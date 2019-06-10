from abc import ABCMeta, abstractmethod

class BaseTask:
	__metaclass__ = ABCMeta

	@abstractmethod
	def start_task(self):
		pass


	@abstractmethod
	def stop_task(self):
		pass