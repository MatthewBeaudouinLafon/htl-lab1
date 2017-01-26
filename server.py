"""
A Flask server that presents a minimal browsable interface for the Olin course catalog.

author: Oliver Steele <oliver.steele@olin.edu>
date  : 2017-01-18
license: MIT
"""

import os
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import pandas as pd
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)

courses = pd.read_csv('./data/olin-courses-16-17.csv')

def prof_string_to_dicts(team):
	""" 
	Takes string of professor(s) from the data's format and makes a list of dict 
	eg: Hoffman, Aaron -> [{'name': 'Aaron Hoffman', 'email':'mailto:aaron.hoffman@olin.edu'}]
	"""
	prof_dicts = []
	if type(team) is not str:
		print("WARN: {} is not a string".format(team))
		return []

	for prof in team.split('; '):
			name = prof.split(', ')
			name.reverse()

			# Takes care of edge case where professors aren't sperated by ';'
			for i in range(0, len(name), 2):
				if name[0] != 'Staff':
					try:
						first_name, last_name = tuple(name[i:i + 2])
					except:
						first_name = name[0]
						last_name = "/".join(name[1:])
						print('Weird looking name:{}, {}'.format(first_name, last_name))
					email = "mailto:{}.{}@olin.edu".format(first_name.lower(), last_name.lower())
					prof_dicts.append({"name": " ".join([first_name, last_name]),
						   			   "email": email})
	return prof_dicts

# Get professors for index page
professors = []
for team in courses.course_contact.dropna():
	if team != "Staff":
		professors += prof_string_to_dicts(team)

professors = {prof['name']:prof for prof in professors}.values()
# Courtesy of http://stackoverflow.com/questions/11092511/python-list-of-unique-dictionaries

# Pre-process area courses
course_dict = {}
for area in set(courses.course_area):
	area_courses = courses[courses.course_area == area].iterrows()
	area_courses_dict = {}

	for index, course in area_courses:
		area_courses_dict[course.course_number] = {"name" : course.course_name,
												   "description" : course.course_description,
												   "professors" : prof_string_to_dicts(course.course_contact)}

	course_dict[area] = area_courses_dict

print(course_dict['AHSE']['AHSE4199'])

# course_dict = {
# 	'AHS': {}
# }

# <dt>{{ course.course_number }}: {{ course.course_name }} ({{ course.course_contact }})</dt>
# <dd>{{ course.course_description }}</dd>

@app.route('/health')
def health():
    return 'ok'

@app.route('/')
def home_page():
    return render_template('index.html', areas=set(courses.course_area), contacts=professors)

@app.route('/area/<course_area>')
def area_page(course_area):
   return render_template('course_area.html', course_area=course_area, courses=course_dict[course_area])  #course_dict[course_area])
   #return render_template('course_area.html', course_area=course_area, courses=courses[courses.course_area == course_area].iterrows())

if __name__ == '__main__':
    app.run(debug=True)
