#!/usr/bin/env python2
import glob
import json
import serial
import sys
import time
import urllib2

def crc(data):
	value=0
	for ii in data:
		value^=ord(ii)
	return chr(value)

def list_serial_ports():
	if sys.platform.startswith('win'):
		ports=['COM%s'%(ii+1) for ii in range(256)]
	elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
		ports=glob.glob('/dev/ttyUSB*')+glob.glob('/dev/ttyACM*')
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

def get_frame():
	try:
		response=urllib2.urlopen('https://your.web.site/?get_frame')
		data=json.loads(response.read())
		data_bytes=''
		if not data:
			return None
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
		return data_bytes
	except Exception as error:
		print('ERROR - '+str(error))
	return None

if __name__=='__main__':
	try:
		print('Starting color viewer')
		while True:
			try:
				serial_port=None
				serial_ports=list_serial_ports()
				for port in serial_ports:
					if port.lower().find('bluetooth')<0:
						serial_port=serial.Serial(port=port,baudrate=115200)
						if serial_port.isOpen():
							print('opened '+port)
						while serial_port.isOpen():
							serial_port.inWaiting()
							frame=get_frame()
							if frame:
								length=serial_port.write('az'+frame+crc(frame))
								if length==len(frame):
									print('sent data '+str(len(frame)))
							time.sleep(0.3)
				time.sleep(1)
			except IOError as error:
				print('disconnected')
	except Exception as error:
		print('ERROR - '+str(error))
	except KeyboardInterrupt:
		exit(1)
