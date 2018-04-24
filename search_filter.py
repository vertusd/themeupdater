class IntegerFilter(object):
	range_min=0
	range_max=100000
	scale=1
	def  __init__(self, range_min, range_max, scale):
		self.range_min = range_min
		self.range_max = range_max
		self.scale = scale
	def __unicode__(self):
		return (range_min, range_max)

class VideoDurationFileter(object):
	range_min=0
	range_max=86400
	#seconds
	scale=1
	def  __init__(self, range_min, range_max, scale):
		self.range_min = range_min
		self.range_max = range_max
		self.scale = scale
	def __unicode__(self):
		return (range_min, range_max)

def divide(data_set, init_filter_list):
	result_filter_list=[]

def search(data_set, filter_list):
	result_set=[]
	for data in data_set:
		is_in_range=True
		for idx in range(0, len(filter_list)):
			if data[idx] >= filter_list[idx].range_min and data[idx] < filter_list[idx].range_max:
				#print "idx:" + str(idx)+ ""
				#print data[idx]
			else:
				is_in_range=False
		if is_in_range == True:
			result_set.append(data)
	return result_set




if __name__ == "__main__":
	data_set=[(1,8600,1),(14,150,2),(12,1900,3),(12,80000,4),(12,125,5),(12,190,6),(11,180,7),(11,520,8),(11,550,9),(11,999,10),(11,80000,11),(111,8000,12),(11,11,13),(11,256,14),(11,998,15),(11,999,16),(11,12345,17),(990,222,18),(12345,555,19),(34567,222,20)]
	int_filter = IntegerFilter(0, 100000, 1)
	vid_filter = VideoDurationFileter(0, 1000, 1)
	filter_list= [int_filter, vid_filter]
	result = search(data_set, filter_list)
	print len(result)
	print len(data_set)
	print result