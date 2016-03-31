from multiprocessing import Process, Lock
from multiprocessing.sharedctypes import Value, Array
from ctypes import Structure, c_double

class Point(Structure):
    _fields_ = [('x', c_double), ('y', c_double)]

def modify(n, x, s, A,test):
	n.value **= 2
	x.value **= 2
	s = s[:6]
	y = []
	for x in xrange(4):
		y.append(x)
		# test[x] = x
		test[x] = y
		print x
		print test[:]
	for a in A:
		a.x **= 2
		a.y **= 2
		

if __name__ == '__main__':
	lock = Lock()

	n = Value('i', 7)
	x = Value(c_double, 1.0/3.0, lock=False)
	s = Array('b', range(10), lock=False)
	A = Array(Point, [(1.875,-6.25), (-5.75,2.0), (2.375,9.5)], lock=lock)
	test = Array('i', [0]*4, lock = lock)

	p = Process(target=modify, args=(n, x, s, A,test))
	p.start()
	p.join()

	print n.value
	print x.value
	print str(s[:])
	print [(a.x, a.y) for a in A]
	print str(test[:])