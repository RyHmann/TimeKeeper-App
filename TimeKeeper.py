import tkinter as tk
import datetime
import time
import sqlite3
from PIL import Image
from PIL import ImageTk

LARGE_FONT = ("Arial", 17)
CLOCK_FONT = ("Bahnschrift Light Condensed", 26)
FLAVOR_FONT = ("Helvetica", 11)



'''
--------------------------------------------------------------------------------------
===================================Application Root===================================
______________________________________________________________________________________
'''
class TimeKeeper(tk.Tk):
	def __init__(self, *args, **kwargs):
		tk.Tk.__init__(self, *args, **kwargs)
		self.iconbitmap('C:/Users/ryanh/OneDrive/Desktop/Python/Projects/TimeKeeper/GUI/TimeKeeperIcon.ico')
		self.title("TimeKeeper")
		self.geometry("300x300")
		'''Task Data temporary storage'''
		self.app_data = {
							"task_name": tk.StringVar(),
							"task_date": 0,
							"start_time": 0,
							"end_time": 0,
							"elapsed_time": 0
						}


		'''Sets a Top and Bottom main Frame'''
		top_container = tk.Frame(self)
		top_container.grid(row=0, column=0)
		bottom_container = tk.Frame(self)
		bottom_container.grid(row=2, column=0)

		'''Loading Top and Bottom Frames into main window'''
		self.top_frames = {}
		for frame in (TopFrame_clock, TopFrame_entry, TopFrame_review):
			top_frame = frame(top_container, self)
			self.top_frames[frame] = top_frame
			top_frame.grid(row=0, column=0, sticky="nsew")

		self.bottom_frames = {}
		for frame in (BottomFrame_record, BottomFrame_stop, BottomFrame_finish, BottomFrame_review):
			bottom_frame = frame(bottom_container, self)
			self.bottom_frames[frame] = bottom_frame
			bottom_frame.grid(row=0, column=0, sticky="nsew")

		'''Loading Top and Bottom Frames into main window'''
		self.show_top_frame(TopFrame_entry)
		self.show_bottom_frame(BottomFrame_record)

	'''Raises selected Top Frame so that it's visible'''	
	def show_top_frame(self,controller):
		frame = self.top_frames[controller]
		frame.tkraise()

	'''Raises selected Bottom Frame so that it's visible'''
	def show_bottom_frame(self, controller):
		frame = self.bottom_frames[controller]
		frame.tkraise()

	def access_top_frame(self, frame):
		return self.top_frames[frame]

	def access_bottom_frame(self, frame):
		return self.bottom_frames[frame]

'''
-----------------------------------------------------------------------------
===================================Widgets===================================
_____________________________________________________________________________
'''

'''=========================Clock Display========================='''
class TopFrame_clock(tk.Frame):
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		self.controller = controller
		clock_label = tk.Label(self, text="Current Task:")
		clock_label.grid(row=0, column=0)
		self.clock = tk.Label(self, text='0h:00m:00s', width=20, font=CLOCK_FONT)
		self.clock.grid(row=1, column=0, columnspan=2, rowspan=1)

	'''
	Updates the Clock text with the elapsed time
	'''
	def update_clock(self):
		#Get current time, plus any elapsed time to account for any 'breaks' for when User presses 'Stop'
		now = time.time() + self.controller.app_data['elapsed_time']
		elapsed_time = now - self.controller.app_data['start_time']
		running_time = self.time_convert(int(elapsed_time))
		self.clock.configure(text=running_time)
		self.refresher = self.after(250, self.update_clock)

	'''
	Converts seconds to Hours, Minutes, and int(Seconds)
	'''
	def time_convert(self, time_elapsed):
		seconds = time_elapsed % 60
		minutes = time_elapsed / 60
		minutes = minutes % 60
		hours = time_elapsed // 3600
		days = hours // 24
		weeks = days // 7
		years = days // 365.25
		return str("{}h {}m {}s".format(int(hours), int(minutes), int(seconds)))

	'''
	Stops self.refreshser in update_clock(self), unable to figure out how to locate this function within BottomFrame_stop
	'''
	def stop_clock(self):
		self.after_cancel(self.refresher)
		


'''=========================Entry Frame========================='''
class TopFrame_entry(tk.Frame):
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		self.controller = controller
		task_label = tk.Label(self, text="I'm going to work on...", font=FLAVOR_FONT)
		task_label.grid(row=0, column=0, sticky = 'sw')
		self.task_entry = tk.Entry(self, textvariable=self.controller.app_data["task_name"], width=20, font=LARGE_FONT, fg="#083D77")
		self.task_entry.insert(0, "Enter task here")
		self.task_entry.grid(row=1, column=0, padx=10, pady=10, columnspan=2)

	def set_name(self):
		self.controller.app_data["task_name"].set(self.task_name)



'''=========================Review Frame========================='''
class TopFrame_review(tk.Frame):
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		self.controller = controller
		self.task_label = tk.Label(self, text='Task')
		self.task_label.grid(row=0, column=0)
		self.time_label = tk.Label(self, text='0h:00m:00s', font=CLOCK_FONT)
		self.time_label.grid(row=1, column=0)
		self.time_today_flavor_label = tk.Label(self, text='Time spent today:')
		self.time_today_flavor_label.grid(row=2, column=0)
		self.time_today_label = tk.Label(self, text='0h:00m:00s', font=CLOCK_FONT)
		self.time_today_label.grid(row=3, column=0)

	def set_review_values(self):
		task_name = self.controller.app_data['task_name'].get()
		self.task_label.configure(text=task_name)
		self.set_review_elapsed_time()
		self.set_review_time_today()


	def set_review_elapsed_time(self):
		elapsed_time = self.controller.app_data['elapsed_time']
		outside_method = self.controller.access_top_frame(TopFrame_clock)
		formatted_time = outside_method.time_convert(elapsed_time)
		self.time_label.configure(text=formatted_time)

	def set_review_time_today(self):
		elapsed_time = self.controller.app_data['elapsed_time']
		task_name = self.controller.app_data['task_name'].get()
		task_date = str(self.controller.app_data['task_date'])
		outside_method = self.controller.access_bottom_frame(BottomFrame_review)
		stored_tasks = outside_method.task_db_query(task_name, task_date)
		stored_time = self.sum_stored_task_times(stored_tasks)
		elapsed_time_today = elapsed_time + stored_time
		outside_method = self.controller.access_top_frame(TopFrame_clock)
		formatted_time = outside_method.time_convert(elapsed_time_today)
		self.time_today_label.configure(text=formatted_time)

	def sum_stored_task_times(self, db_query):
		if db_query == []:
			return 0
		else:
			for x in db_query:
				times = [x[4] for x in db_query]
				sum_times = 0
				for x in times:
					sum_times += x
			return sum_times
		



'''=========================Initialize Frame========================='''
#Initiates the Timer
class BottomFrame_record(tk.Frame):
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		self.controller = controller
		record_button = tk.Button(self, text='Record', command=self.start_time)
		record_button.grid(row=0, column=0,padx=30, pady=30)

	'''
	Initiates timer and logs start_time, date into app_data
	'''
	def start_time(self):
		start_time = time.time()
		self.controller.app_data["start_time"] = start_time
		self.controller.app_data['task_date'] = datetime.date.today()
		self.controller.show_bottom_frame(BottomFrame_stop)
		self.controller.show_top_frame(TopFrame_clock)

		#Calls method from access_top_frame class
		outside_method_clock = self.controller.access_top_frame(TopFrame_clock)
		outside_method_clock.update_clock()



'''=========================Recording Frame========================='''
#Stops the Timer
class BottomFrame_stop(tk.Frame):
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		self.controller = controller
		stop_button = tk.Button(self, text='Stop', command=self.stop_time)
		stop_button.pack()

	'''Stop Button Methods'''
	def stop_time(self):
		pause_time = time.time()
		outside_method = self.controller.access_top_frame(TopFrame_clock)
		outside_method.stop_clock()
		self.controller.app_data["elapsed_time"] = self.controller.app_data["elapsed_time"] + (pause_time - self.controller.app_data["start_time"])
		self.controller.show_bottom_frame(BottomFrame_finish)



'''=========================Paused Frame========================='''
#Timer is stopped user has choice to Resume or Finish Task
class BottomFrame_finish(tk.Frame):
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		self.controller = controller
		record_button = tk.Button(self, text='Continue', command=self.resume_time)
		record_button.grid(row=0, column=0)
		save_button = tk.Button(self, text='Finish', command=self.finish_task)
		save_button.grid(row=0, column=1)

	'''Resume Button Methods'''
	def resume_time(self):
		self.controller.show_bottom_frame(BottomFrame_stop)
		outside_method = self.controller.access_bottom_frame(BottomFrame_record)
		outside_method.start_time()

	'''Finish Button Methods'''
	def finish_task(self):
		self.controller.show_bottom_frame(BottomFrame_review)
		self.controller.show_top_frame(TopFrame_review)
		self.controller.app_data["end_time"] = time.time()
		outside_method = self.controller.access_top_frame(TopFrame_review)
		outside_method.set_review_values()



'''=========================Save-Edit Frame========================='''
#Saves app_data to database, or discards current task
class BottomFrame_review(tk.Frame):
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		self.controller = controller
		save_button = tk.Button(self, text='Save', command=self.save_task)
		save_button.grid(row=0, column=1)
		discard_button = tk.Button(self, text='Discard', command=self.discard_task)
		discard_button.grid(row=0, column=0)
		#Database variables
		self.conn = sqlite3.connect('task.db')
		self.c = self.conn.cursor()

	'''Save Button Methods'''
	def save_task(self):
		self.controller.show_bottom_frame(BottomFrame_record)
		self.controller.show_top_frame(TopFrame_entry)
		task = self.app_data_parse()
		self.app_data_to_db(task)
		self.reset_app_data()


	def app_data_parse(self):
		app_data_dict = {
					"task_name": str(self.controller.app_data["task_name"].get()).strip(),
					"task_date": str(self.controller.app_data["task_date"]),
					"start_time": int(self.controller.app_data["start_time"]),
					"end_time": int(self.controller.app_data["end_time"]),
					"elapsed_time": int(self.controller.app_data["elapsed_time"])
						}
		return app_data_dict

	'''
	SQL Table Creation
	def create_db(self):
		self.c.execute("""CREATE TABLE tasks (
		task_name text collate nocase,
		task_date text,
		start_time integer,
		end_time integer,
		elapsed_time integer
		)""")
	'''


	def app_data_to_db(self, task_dict):
		with self.conn:
			self.c.execute("INSERT INTO tasks VALUES (:task_name, :task_date, :start_time, :end_time, :elapsed_time)", 
			{'task_name':task_dict['task_name'], 
			'task_date':task_dict['task_date'], 
			'start_time':task_dict['start_time'],
			'end_time':task_dict['end_time'],
			'elapsed_time':task_dict['elapsed_time']
			})

	def task_db_query(self, name_to_find, date_to_find):
		with self.conn:
			self.c.execute("SELECT * FROM tasks WHERE task_name=:task_name AND task_date=:task_date", {'task_name':name_to_find, 'task_date':date_to_find})
			return self.c.fetchall()

	def reset_app_data(self):
		self.controller.app_data['task_date'] = 0
		self.controller.app_data['start_time'] = 0
		self.controller.app_data['end_time'] = 0
		self.controller.app_data['elapsed_time'] = 0

	'''Discard Button Methods'''
	def discard_task(self):
		self.controller.show_bottom_frame(BottomFrame_record)
		self.controller.show_top_frame(TopFrame_entry)
		self.reset_app_data()


'''=========================Main========================='''
def main():
	app = TimeKeeper()
	app.mainloop()


if __name__ == '__main__':
	main()