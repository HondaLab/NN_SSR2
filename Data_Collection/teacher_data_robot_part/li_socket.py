import socket

robot_address = '172.16.7.101'
sensor_port = 50005
send_buf_size = 6000
recv_buf_size = 300


#soc.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,recv_buf_size)


#bufsize_recv = soc.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)



class UDP_Send():
	def __init__(self,addr,port):
		self.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.soc.setsockopt(socket.SOL_SOCKET,socket.SO_SNDBUF,send_buf_size)
		self.bufsize_send = self.soc.getsockopt(socket.SOL_SOCKET,socket.SO_SNDBUF)
		self.addr = addr
		self.port = port	
		print(self.bufsize_send)
	def send(self,lis):
		strig = ''
		num = len(lis)
		i = 0
		while i<num:
			strig = strig + str("%12.8f"%lis[i])
			if i != num-1:
				strig = strig+','
			i = i+1
		self.sock.sendto(strig.encode('utf-8'),(self.addr,self.port))
		return 0
		
class UDP_Recv():
	def __init__(self,addr,port):
		self.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		self.sock.bind((addr,port))
		self.sock.setblocking(0)
		self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.soc.setsockopt(socket.SOL_SOCKET,socket.SO_SNDBUF,recv_buf_size)
		self.bufsize_recv = self.soc.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
		#print(self.bufsize_recv)
	def recv(self):
		message = self.sock.recv(1024).decode('utf-8')
		slist = message.split(',')
		a = [float(s) for s in slist]
		return a
