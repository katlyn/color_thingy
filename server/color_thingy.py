#!/usr/bin/env python
import BaseHTTPServer
import glob
import json
import mimetypes
import os
import serial
import SimpleHTTPServer
import sys
import threading
import time
import urllib
import urlparse

frame_data=''
serial_needs_written=False
serial_mutex=threading.Lock()

deadman_mutex=threading.Lock()
main_dead=False

def crc(data):
	value=0
	for ii in data:
		value^=ord(ii)
	return chr(value)

def list_serial_ports():
	if sys.platform.startswith('win'):
		ports=['COM%s'%(ii+1) for ii in range(256)]
	elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
		ports=glob.glob('/dev/tty[A-Za-z]*')
	elif sys.platform.startswith('darwin'):
		ports=glob.glob('/dev/tty.*')
	else:
		raise EnvironmentError('Unsupported platform')
	serial_ports=[]
	for port in ports:
		try:
			serial_port=serial.Serial(port)
			serial_port.close()
			serial_ports.append(port)
		except(OSError,serial.SerialException):
			pass
	return serial_ports

def deadman_check():
	global deadman_mutex
	global main_dead
	deadman_mutex.acquire()
	is_dead=main_dead
	deadman_mutex.release()
	return is_dead

def serial_handler():
	while True:
		try:
			if deadman_check():
				break
			serial_port=None
			serial_ports=list_serial_ports()
			for port in serial_ports:
				if port.lower().find('bluetooth')<0:
					serial_port=serial.Serial(port=port,baudrate=115200)
					if serial_port.isOpen():
						print('opened '+port)
					while serial_port.isOpen():
						serial_port.inWaiting()
						if deadman_check():
							break
						data=read_serial_data()
						if not data[0]:
							continue
						length=serial_port.write('az'+data[1]+crc(data[1]))
						if length==len(data[1]):
							print('sent data '+str(len(data[1])))
							clear_serial_data()
			time.sleep(1)
		except IOError as error:
			print('disconnected')
		except Exception as error:
			print(error)

def send_serial_data(data):
	global frame_data
	global serial_needs_written
	global serial_mutex
	serial_mutex.acquire()
	frame_data=data
	serial_needs_written=True
	serial_mutex.release()

def read_serial_data():
	global frame_data
	global serial_needs_written
	global serial_mutex
	serial_mutex.acquire()
	ret_data=(serial_needs_written,frame_data)
	serial_mutex.release()
	return ret_data

def clear_serial_data():
	global frame_data
	global serial_needs_written
	global serial_mutex
	serial_mutex.acquire()
	serial_needs_written=False
	frame_data=''
	serial_mutex.release()

class MyHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
	def do_GET(self):
		try:
			self.path=self.path.split('?')
			query_str='?'.join(self.path[1:])
			if len(query_str)>0:
				query_str='?'+query_str
			self.path=self.path[0]
			if len(self.path)>0 and self.path[-1]=='/':
				self.path+='index.html'
			cwd=os.getcwd()+'/web/'
			self.path=os.path.abspath(cwd+self.path)
			if self.path.find(cwd)!=0 or not os.path.isfile(self.path):
				self.send_response(404)
				self.end_headers()
				return
			file=open(self.path,'r')
			self.send_response(200)
			mime=mimetypes.guess_type(self.path)
			if len(mime)>0:
				mime=mime[0]
			else:
				mime='text/plain'
			print(mime+' '+self.path)
			self.send_header('Content-type',mime)
			self.end_headers()
			self.wfile.write(file.read())
			self.wfile.close()
		except Exception as error:
			self.send_response(401)

	def do_POST(self):
		try:
			data_len=int(self.headers.getheader('content-length',0))
			if data_len>2e6:
				self.send_response(413)
				self.end_headers()
			try:
				data=self.rfile.read(data_len)
				data=json.loads(data)
				data_bytes=''
				if not isinstance(data,list):
					raise Exception('Not a list.')
				if len(data)!=8:
					raise Exception('Invalid frame.')
				for yy in range(0,len(data)):
					if not isinstance(data[yy],list):
						raise Exception('Invalid frame.')
					if len(data[yy])!=8:
						raise Exception('Invalid frame.')
					for xx in range(0,len(data[yy])):
						if not isinstance(data[yy][xx],list):
							raise Exception('Invalid frame.')
						if len(data[yy][xx])!=3:
							raise Exception('Invalid frame.')
						for ii in range(0,len(data[yy][xx])):
							if not isinstance(data[yy][xx][ii],int):
								raise Exception('Invalid frame.')
							if data[yy][xx][ii]<0 or data[yy][xx][ii]>255:
								raise Exception('Invalid frame.')
							data_bytes+=chr(data[yy][xx][ii])
				send_serial_data(data_bytes)
			except Exception as error:
				print(error)
				self.send_response(400)
				self.end_headers()
				return
			self.send_response(200)
			self.send_header('Content-type','application/javascript')
			self.end_headers()
			self.wfile.close()
		except Exception as error:
			self.send_response(401)
			self.end_headers()

if __name__=='__main__':
	try:
		thread=threading.Thread(target=serial_handler)
		thread.start()
		Handler=MyHandler
		server=BaseHTTPServer.HTTPServer(('0.0.0.0',8080),MyHandler)
		server.serve_forever()
	except Exception as error:
		print('ERROR - '+str(error))
	except KeyboardInterrupt:
		print('interrupt')
		deadman_mutex.acquire()
		main_dead=True
		deadman_mutex.release()
