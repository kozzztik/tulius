from django.db.models import Max, Min
import random

def generate_random_id(id_length = 50, characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890'):
	id = ''
	for y in range(id_length):
		id += characters[random.randint(0, len(characters)-1)]
	return id

import os

def rel(*x):
	return os.path.join(os.path.abspath(os.path.dirname(__file__)), *x)

CREATION_YEAR_CHOICES = (
	(1990, 1990),
	(1991, 1991),
	(1992, 1992),
	(1993, 1993),
	(1994, 1994),
	(1995, 1995),
	(1996, 1996),
	(1997, 1997),
	(1998, 1998),
	(1999, 1999),
	(2000, 2000),
	(2001, 2001),
	(2002, 2002),
	(2003, 2003),
	(2004, 2004),
	(2005, 2005),
	(2006, 2006),
	(2007, 2007),
	(2008, 2008),
	(2009, 2009),
	(2010, 2010),
	(2011, 2011),
	(2012, 2012),
	(2013, 2013),
	(2014, 2014),
	(2015, 2015),
	(2016, 2016),
	(2017, 2017),
	(2018, 2018),
	(2019, 2019),
	(2020, 2020),
	(2021, 2021),
	(2022, 2022),
	(2023, 2023),
	(2024, 2024),
	(2025, 2025),
	(2026, 2026),
	(2027, 2027),
	(2028, 2028),
	(2029, 2029),
	(2030, 2030),
	(2031, 2031),
	(2032, 2032),
	(2033, 2033),
	(2034, 2034),
	(2035, 2035),
	(2036, 2036),
	(2037, 2037),
	(2038, 2038),
	(2039, 2039),
	(2040, 2040),
	(2041, 2041),
	(2042, 2042),
	(2043, 2043),
	(2044, 2044),
	(2045, 2045),
	(2046, 2046),
	(2047, 2047),
	(2048, 2048),
	(2049, 2049),
)

def do_gauss_analyze(query, field_name, intervals):
	values = query.aggregate(model_min=Min(field_name), model_max=Max(field_name))
	min_val = values['model_min']
	max_val = values['model_max']
	delta = (float(max_val - min_val) / intervals)
	data = []
	for i in range(intervals):
		interval_start = int(min_val + (delta * i))
		interval_end = int(min_val + (delta * (i + 1)))
		subquery = {field_name + '__gte': interval_start}
		if i == intervals - 1:
			subquery[field_name + '__lte'] = interval_end
		else: 
			subquery[field_name + '__lt'] = interval_end
		data += [('%s - %s' % (interval_start, interval_end), query.filter(**subquery).count())]
	return data