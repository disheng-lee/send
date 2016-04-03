import itertools
def g():
	print('--start--')
	for i in itertools.count():
		print('--yielding %i--' % i)
		try:
			ans = yield i
		except GeneratorExit:
			print('--closing--')
			raise
		except Exception as e:
			print('--yield raised %r' %e)
		else:
			print('---yield return %s---'%ans)