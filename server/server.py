#!/usr/bin/env python
import BaseHTTPServer
import json
import os
import mimetypes
import SimpleHTTPServer

last_frame=None
frame_height=8
frame_width=8

class MyHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
	global last_frame
	def do_GET(self):
		try:
			self.path=self.path.split('?')
			query_str='?'.join(self.path[1:])
			if len(query_str)>0:
				query_str='?'+query_str
			if query_str=='?get_frame':
				self.send_response(200)
				self.send_header('Content-type','application/json')
				self.end_headers()
				self.wfile.write(json.dumps(last_frame))
				self.wfile.close()
				return
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
			print(error)
			self.send_response(401)

	def do_POST(self):
		global last_frame
		global frame_height
		global frame_width
		try:
			data_len=int(self.headers.getheader('content-length',0))
			if data_len>2e6:
				self.send_response(413)
				self.end_headers()
			try:
				frame=self.rfile.read(data_len)
				frame=json.loads(frame)
				if not isinstance(frame,list):
					raise Exception('Not a list.')
				if len(frame)!=frame_height:
					raise Exception('Invalid frame.')
				for yy in range(0,len(frame)):
					if not isinstance(frame[yy],list):
						raise Exception('Invalid frame.')
					if len(frame[yy])!=frame_width:
						raise Exception('Invalid frame.')
					for xx in range(0,len(frame[yy])):
						if not isinstance(frame[yy][xx],list):
							raise Exception('Invalid frame.')
						if len(frame[yy][xx])!=3:
							raise Exception('Invalid frame.')
						for ii in range(0,len(frame[yy][xx])):
							if not isinstance(frame[yy][xx][ii],int):
								raise Exception('Invalid frame.')
							if frame[yy][xx][ii]<0 or frame[yy][xx][ii]>255:
								raise Exception('Invalid frame.')
				last_frame=frame
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
		print('Starting color server')
		Handler=MyHandler
		server=BaseHTTPServer.HTTPServer(('127.0.0.1',8080),MyHandler)
		server.serve_forever()
	except Exception as error:
		print('ERROR - '+str(error))
	except KeyboardInterrupt:
		exit(1)
