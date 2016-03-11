from multiprocessing import Process, Manager

def f(messages):
	roll = []
	yaw = []
	# attitude = dict()
	for i in xrange(10):
		roll.append(i)
		yaw.append(i*2)
	messages['Attitude'] = {'Roll': roll,'Yaw': yaw}
	messages['bleh'] = {'Roll': roll,'Yaw': yaw}
	#attitude['Roll'] = roll
	# messages['Attitude'] = attitude['Roll']
	#messages['Attitude']['Roll'] = roll
	#print 'Roll:'
	#print messages['Attitude']
	
	#attitude['Yaw'] = yaw
	#messages['Attitude'] = attitude['Yaw']
	# print 'Yaw:'
	#print messages['Attitude']['Yaw']
	# print attitude
	print messages
	

if __name__ == '__main__':
	manager = Manager()
	
	messages = manager.dict()
	#messages = {'Roll': [],'Yaw': []}
	#messages['Roll'] = []
	#messages['Yaw'] = []
	#d = {'Roll': , 'Yaw': }
	#d['Roll'] = 
	#d['Yaw'] = []
	
	p1 = Process(target=f, args=(messages,))
	p2 = Process(target=f, args=(messages,))
	p1.start()
	p2.start()
	p1.join()
	p2.join()
	# print 'Messages:'
	#print messages
	# print 'Roll'
	print messages['Attitude']['Roll']
	print messages['bleh']['Roll']
	# print 'Yaw'
	# print messages['Yaw']