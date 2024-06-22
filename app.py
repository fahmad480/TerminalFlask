from flask import Flask, render_template, request, redirect, url_for, Response, jsonify
# from flask_ngrok import run_with_ngrok
import sys
import logging
import time
import threading
import psutil
import signal

app = Flask(__name__)
# run_with_ngrok(app)

# Membuat logger khusus untuk aplikasi
app_logger = logging.getLogger('AppLogger')
app_logger.setLevel(logging.INFO)
handler = logging.FileHandler('app.log')
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
handler.setFormatter(formatter)
app_logger.addHandler(handler)

thread1 = threading.Thread()

# Mengalihkan print ke logger khusus agar bisa ditampilkan di web
class StreamToLogger(object):
    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

    def flush(self):
        pass

sys.stdout = StreamToLogger(app_logger, logging.INFO)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/form', methods=['POST'])
def form():
    nilai_variabel = request.form['variabel']
    print(f"Nilai variabel diubah menjadi: {nilai_variabel}")
    return redirect(url_for('index'))

@app.route('/logs')
def logs():
    with open('app.log', 'r') as log_file:
        lines = log_file.readlines()
    last_100_lines = lines[-100:] if len(lines) > 100 else lines
    content = ''.join(last_100_lines)
    return Response(content, mimetype='text/plain')

@app.route('/usage/load')
def load_usage():
    load1, load5, load15 = psutil.getloadavg()  # Mendapatkan rata-rata beban sistem
    return jsonify(load1=load1, load5=load5, load15=load15)

@app.route('/usage/cpu')
def cpu_usage():
    cpu_percent = psutil.cpu_percent(interval=1)  # Mendapatkan penggunaan CPU
    return jsonify(cpu_percent=cpu_percent)

@app.route('/usage/ram')
def ram_usage():
    ram = psutil.virtual_memory()  # Mendapatkan penggunaan RAM
    return jsonify(total=ram.total, available=ram.available, percent=ram.percent)

# app route to stop thread1
@app.route('/stop/thread1')
def stop_thread1():
    global thread1
    thread1.join()
    print("Thread1 stopped")
    return jsonify(message="Thread1 stopped")

def test():
    while True:
        print("Test")
        time.sleep(1)

if __name__ == '__main__':
    # Jalankan fungsi test di thread terpisah
    # thread1 = threading.Thread(target=test)
    # thread1.start()

    app.run(debug=False, port=5001)