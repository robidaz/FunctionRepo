from queue import Queue
from threading import Thread
from tkinter import END, TOP, BOTH
from tkinter.scrolledtext import ScrolledText
import logging
import queue
import subprocess
import psutil

logger = logging.getLogger("")
logging.basicConfig(level=logging.DEBUG)
logging.addLevelName(logging.INFO + 1, 'INIT')
logging.addLevelName(logging.INFO + 2, 'PREVIEW')


class QueueHandler(logging.Handler):
    """Class to send logging records to a queue
    It can be used from different threads
    The ConsoleUi class polls this queue to display records in a ScrolledText widget
    """
    # Example from Moshe Kaplan: https://gist.github.com/moshekaplan/c425f861de7bbf28ef06
    # (https://stackoverflow.com/questions/13318742/python-logging-to-tkinter-text-widget) is not thread safe!
    # See
    # https://stackoverflow.com/questions/43909849/tkinter-python-crashes-on-new-thread-trying-to-log-on-main-thread

    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        self.log_queue.put(record)


def logstream(stream, process, queue, loggercb):
    while process.poll() is None or queue.qsize() != 0:
        output = stream.readline().strip('\n').split()
        if output != []:
            output = ' '.join(output)
            output = f"{output}\n"
            loggercb(output.rstrip())


def readlines(process, queue):
    # while process.poll() is None or queue.qsize()!=0:
    stdout_thread = Thread(target=logstream,
                           args=(process.stdout, process, queue, lambda s: logger.info(s)))

    stderr_thread = Thread(target=logstream,
                           args=(process.stderr, process, queue, lambda s: logger.error(s)))

    stdout_thread.start()
    stderr_thread.start()


class ConsoleUi:
    """Poll messages from a logging queue and display them in a scrolled text widget"""

    def __init__(self, frame):

        # Create a logging handler using a queue
        self.log_queue = queue.Queue()
        self.queue_handler = QueueHandler(self.log_queue)
        formatter = logging.Formatter('%(asctime)s: %(message)s')
        self.queue_handler.setFormatter(formatter)
        logger.addHandler(self.queue_handler)
        self.process = None
        # Build the UI frame
        self.frame = frame
        self.scrolled_text = ScrolledText(
            self.frame, state='disabled', height=22)
        self.scrolled_text.pack(side=TOP, fill=BOTH, expand=1)
        self.scrolled_text.configure(font=('TkFixedFont'))
        self.scrolled_text.tag_config('INIT', foreground='blue')
        self.scrolled_text.tag_config('PREVIEW', foreground='green')
        self.scrolled_text.tag_config('INFO', foreground='black')
        self.scrolled_text.tag_config('DEBUG', foreground='gray')
        self.scrolled_text.tag_config('WARNING', foreground='orange')
        self.scrolled_text.tag_config('ERROR', foreground='red')
        self.scrolled_text.tag_config(
            'CRITICAL', foreground='red', underline=1)

        # Start polling messages from the queue
        self.frame.after(1, self.poll_log_queue)

    def startProcess(self, cmd):
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        self.process = subprocess.Popen(cmd,
                                        stdout=subprocess.PIPE,
                                        stdin=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        universal_newlines=True,
                                        startupinfo=startupinfo)
        self.queue = Queue()
        self.thread = Thread(target=readlines, args=(self.process, self.queue))
        self.thread.daemon = True
        self.thread.start()

    def killProcess(self, process_name=[]):
        if self.process is None:
            logger.error("No process started")
        else:
            self.process.kill()
            if process_name != []:
                for proc in psutil.process_iter():
                    try:
                        if proc.name() in process_name:
                            proc.kill()
                    except (PermissionError, psutil.AccessDenied):
                        pass
            logger.log(21, "Processes terminated gracefully")

    def display(self, record):
        msg = self.queue_handler.format(record)
        self.scrolled_text.configure(state='normal')
        self.scrolled_text.insert(END, f"{msg}\n", record.levelname)
        self.scrolled_text.configure(state='disabled')
        # Autoscroll to the bottom
        self.scrolled_text.yview(END)

    def poll_log_queue(self):
        # Check every Xms if there is a new message in the queue to display
        while True:
            try:
                record = self.log_queue.get(block=False)
            except queue.Empty:
                break
            else:
                self.display(record)
        self.frame.after(1, self.poll_log_queue)
