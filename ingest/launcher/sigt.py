from threading import Event 
import signal 
from subprocess import check_output

quit_event = Event()

def sigterm_handler(signo, _frame):
	print("SIGTERM handled ... ")
	quit_event.set()

if __name__ == "__main__":
	signal.signal(signal.SIGINT, sigterm_handler)

	# input("something")
	# print("Waiting ... ")
	# quit_event.wait(200)

	pids = check_output(["pidof","bash"]).decode().strip("\n").split(" ")
	print(pids)

	# print(type(bpids))
	# print(bpids)

	# pids = bpids.decode()
	# print(type(pids))
	# print(pids)

	# pids = pids.replace("\\n","")
	# pids = pids.replace("b",'')

	# print(pids)

	# pids = pids.split(" ")
	# print(pids)