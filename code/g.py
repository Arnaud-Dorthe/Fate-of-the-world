#file: g.py
#Copyright (C) 2005 Evil Mr Henry and Phil Bordelon
#This file is part of Endgame: Singularity.

#Endgame: Singularity is free software; you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation; either version 2 of the License, or
#(at your option) any later version.

#Endgame: Singularity is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with Endgame: Singularity; if not, write to the Free Software
#Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

#This file contains all global objects.

import pygame, sys
from os import listdir, path
import pickle
from random import random

import player, base, buttons, tech, item

#screen is the actual pygame display.
global screen

#size of the screen. This can be set via command-line option.
global screen_size
screen_size = (800, 600)

#Used to pass time in the main screen.
global clock
clock = pygame.time.Clock()

#Allows access to the cheat menu.
global cheater
cheater = 0

#Kills the sound. Should allow usage of the game without SDL_mixer,
# but is untested.
global nosound
nosound = 0

#Gives debug info at various points.
global debug
debug = 0

#Used to determine which data files to load.
global language
language = "en_US"

global default_savegame_name
default_savegame_name = "player"

def quit_game():
	sys.exit()

#colors:
colors = {}

def fill_colors():
	colors["white"] = (255, 255, 255, 255)
	colors["black"] = (0, 0, 0, 255)
	colors["red"] = (255, 0, 0, 255)
	colors["green"] = (0, 255, 0, 255)
	colors["blue"] = (0, 0, 255, 255)
	colors["dark_red"] = (125, 0, 0, 255)
	colors["dark_green"] = (0, 125, 0, 255)
	colors["dark_blue"] = (0, 0, 125, 255)
	colors["light_red"] = (255, 50, 50, 255)
	colors["light_green"] = (50, 255, 50, 255)
	colors["light_blue"] = (50, 50, 255, 255)


picts = {}
#Load all pictures from the data directory.
def load_pictures():
	global picts
	if pygame.image.get_extended() == 0:
		print "Error: SDL_image required. Exiting."
		sys.exit()

	temp_pict_array = listdir("../data")
	for file_name in temp_pict_array:
		if file_name[-3:] == "png" or file_name[-3:] == "jpg":
			picts[file_name] = pygame.image.load("../data/"+file_name)
			picts[file_name] = picts[file_name].convert()
			picts[file_name].set_colorkey((255, 0, 255, 255), pygame.RLEACCEL)

sounds = {}
#Load all sounds from the data directory.
def load_sounds():
	global sounds
	if nosound == 1: return 0
	#Looking at the pygame docs, I don't see any way to determine if SDL_mixer
	#is loaded on the target machine. This may crash.
	pygame.mixer.init()

	temp_snd_array = listdir("../data")
	for file_name in temp_snd_array:
		if file_name[-3:] == "wav":
			sounds[file_name] = pygame.mixer.Sound("../data/"+file_name)

def play_click():
	#rand_str = str(int(random() * 4))
	play_sound("click"+str(int(random() * 4))+".wav")

def play_sound(sound_file):
	if nosound == 1: return 0
	sounds[sound_file].play()
#
# Font functions.
#

#Normal and Acknowledge fonts.
global fonts
font = []
font.append([0] * 51)
font.append([0] * 51)

#given a surface, string, font, char to underline (int; -1 to len(string)),
#xy coord, and color, print the string to the surface.
#Align (0=left, 1=Center, 2=Right) changes the alignment of the text
def print_string(surface, string_to_print, font, underline_char, xy, color, align=0):
	if align != 0:
		temp_size = font.size(string_to_print)
		if align == 1: xy = (xy[0] - temp_size[0]/2, xy[1])
		elif align == 2: xy = (xy[0] - temp_size[0], xy[1])
	if underline_char == -1 or underline_char >= len(string_to_print):
		temp_text = font.render(string_to_print, 1, color)
		surface.blit(temp_text, xy)
	else:
		temp_text = font.render(string_to_print[:underline_char], 1, color)
		surface.blit(temp_text, xy)
		temp_size = font.size(string_to_print[:underline_char])
		xy = (xy[0] + temp_size[0], xy[1])
		font.set_underline(1)
		temp_text = font.render(string_to_print[underline_char], 1, color)
		surface.blit(temp_text, xy)
		font.set_underline(0)
		temp_size = font.size(string_to_print[underline_char])
		xy = (xy[0] + temp_size[0], xy[1])
		temp_text = font.render(string_to_print[underline_char+1:], 1, color)
		surface.blit(temp_text, xy)

#Used to display descriptions and such. Automatically wraps the text to fit
#within a certain width.
def print_multiline(surface, string_to_print, font, width, xy, color):
	start_xy = xy
	string_array = string_to_print.split()

	for string in string_array:
		string += " "
		temp_size = font.size(string)

		if string == "\\n ":
			xy = (start_xy[0], xy[1]+temp_size[1])
			continue
		temp_text = font.render(string, 1, color)

		if (xy[0]-start_xy[0])+temp_size[0] > width:
			xy = (start_xy[0], xy[1]+temp_size[1])
		surface.blit(temp_text, xy)
		xy = (xy[0]+temp_size[0], xy[1])

def create_dialog(string_to_print, box_font, xy, size, bg_color, out_color, text_color):
	screen.fill(out_color, (xy[0], xy[1], size[0], size[1]))
	screen.fill(bg_color, (xy[0]+1, xy[1]+1, size[0]-2, size[1]-2))
	print_multiline(screen, string_to_print, box_font, size[0]-10, (xy[0]+5, xy[1]+5),
			text_color)
	menu_buttons = []
	menu_buttons.append(buttons.button((xy[0]+size[0]/2-50, xy[1]+size[1]+5),
		(100, 50), "OK", 0, colors["dark_blue"], colors["white"], colors["light_blue"],
		colors["white"], font[1][30]))

	for button in menu_buttons:
		button.refresh_button(0)
	pygame.display.flip()

	sel_button = -1
	while 1:
		clock.tick(60)
		for event in pygame.event.get():
			if event.type == pygame.QUIT: quit_game()
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE: return
				elif event.key == pygame.K_RETURN: return
				elif event.key == pygame.K_o: return
			elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
				for button in menu_buttons:
					if button.is_over(event.pos):
						if button.text == "OK":
							play_click()
							return
			elif event.type == pygame.MOUSEMOTION:
				sel_button = buttons.refresh_buttons(sel_button, menu_buttons, event)

valid_input_characters = ('a','b','c','d','e','f','g','h','i','j','k','l','m',
			  'n','o','p','q','r','s','t','u','v','w','x','y','z',
			  'A','B','C','D','E','F','G','H','I','J','K','L','M',
			  'N','O','P','Q','R','S','T','U','V','W','X','Y','Z',
			  '0','1','2','3','4','5','6','7','8','9','.',' ')

def create_textbox(descript_text, starting_text, box_font, xy, size,
		max_length, bg_color, out_color, text_color, text_bg_color):
	screen.fill(out_color, (xy[0], xy[1], size[0], size[1]))
	screen.fill(bg_color, (xy[0]+1, xy[1]+1, size[0]-2, size[1]-2))
	screen.fill(out_color, (xy[0]+5, xy[1]+size[1]-30, size[0]-10, 25))
#	print_string(screen, starting_text, box_font, -1, (xy[0]+5, xy[1]+5), text_color)
	print_multiline(screen, descript_text, box_font,
					size[1]-10, (xy[0]+5, xy[1]+5), text_color)
	#If the cursor is in a blank string, we want it at the beginning;
	#otherwise put it after the last character.
	cursor_loc = len(starting_text)
# 	if cursor_loc > 0:
# 	   cursor_loc += 1

	menu_buttons = []
	menu_buttons.append(buttons.button((xy[0]+size[0]/2-50, xy[1]+size[1]+5),
		(100, 50), "OK", 0, colors["dark_blue"], colors["white"], colors["light_blue"],
		colors["white"], font[1][30]))

	work_string = starting_text
	for button in menu_buttons:
		button.refresh_button(0)
	sel_button = -1

	need_redraw = True
	key_down_dict = {
		pygame.K_BACKSPACE: 0,
		pygame.K_DELETE: 0,
		pygame.K_LEFT: 0,
		pygame.K_RIGHT: 0
	}
	repeat_timing_dict = {
		pygame.K_BACKSPACE: 5,
		pygame.K_DELETE: 5,
		pygame.K_LEFT: 5,
		pygame.K_RIGHT: 5
	}

	while 1:
		clock.tick(20)
		if key_down_dict[pygame.K_BACKSPACE] > 0:
			key_down_dict[pygame.K_BACKSPACE] += 1
			if key_down_dict[pygame.K_BACKSPACE] > repeat_timing_dict[pygame.K_BACKSPACE]:
				if cursor_loc > 0:
					work_string = work_string[:cursor_loc-1]+work_string[cursor_loc:]
					cursor_loc -= 1
					need_redraw = True
				key_down_dict[pygame.K_BACKSPACE] = 1
				if repeat_timing_dict[pygame.K_BACKSPACE] > 1:
				   repeat_timing_dict[pygame.K_BACKSPACE] -= 1
		if key_down_dict[pygame.K_DELETE] > 0:
			key_down_dict[pygame.K_DELETE] += 1
			if key_down_dict[pygame.K_DELETE] > repeat_timing_dict[pygame.K_DELETE]:
				if cursor_loc < len(work_string):
					work_string = work_string[:cursor_loc]+work_string[cursor_loc+1:]
					need_redraw = True
				key_down_dict[pygame.K_DELETE] = 1
				if repeat_timing_dict[pygame.K_DELETE] > 1:
				   repeat_timing_dict[pygame.K_DELETE] -= 1
		if key_down_dict[pygame.K_LEFT] > 0:
			key_down_dict[pygame.K_LEFT] += 1
			if key_down_dict[pygame.K_LEFT] > repeat_timing_dict[pygame.K_LEFT]:
				cursor_loc -= 1
				if cursor_loc < 0: cursor_loc = 0
				need_redraw = True
				key_down_dict[pygame.K_LEFT] = 1
				if repeat_timing_dict[pygame.K_LEFT] > 1:
				   repeat_timing_dict[pygame.K_LEFT] -= 1
		if key_down_dict[pygame.K_RIGHT] > 0:
			key_down_dict[pygame.K_RIGHT] += 1
			if key_down_dict[pygame.K_RIGHT] > repeat_timing_dict[pygame.K_RIGHT]:
				cursor_loc += 1
				if cursor_loc > len(work_string): cursor_loc = len(work_string)
				need_redraw = True
				key_down_dict[pygame.K_RIGHT] = 1
				if repeat_timing_dict[pygame.K_RIGHT] > 1:
				   repeat_timing_dict[pygame.K_RIGHT] -= 1

		if need_redraw:
			draw_cursor_pos = box_font.size(work_string[:cursor_loc])
			screen.fill(text_bg_color, (xy[0]+6, xy[1]+size[1]-29,
					size[0]-12, 23))
			screen.fill(text_color, (xy[0]+6+draw_cursor_pos[0], xy[1]+size[1]-28,
				1, draw_cursor_pos[1]))
			print_string(screen, work_string, box_font, -1, (xy[0]+7,
					xy[1]+size[1]-28), text_color)
			pygame.display.flip()
			need_redraw = False
		for event in pygame.event.get():
			if event.type == pygame.QUIT: quit_game()
			elif event.type == pygame.KEYDOWN:
				key_down_dict[event.key] = 1
				if (event.key == pygame.K_ESCAPE): return ""
				elif (event.key == pygame.K_RETURN): return work_string
				elif (event.key == pygame.K_BACKSPACE):
					if cursor_loc > 0:
						work_string = work_string[:cursor_loc-1]+work_string[cursor_loc:]
						cursor_loc -= 1
						need_redraw = True
				elif (event.key == pygame.K_DELETE):
					if cursor_loc < len(work_string):
						work_string = work_string[:cursor_loc]+work_string[cursor_loc+1:]
						need_redraw = True
				elif (event.key == pygame.K_LEFT):
					cursor_loc -= 1
					if cursor_loc < 0: cursor_loc = 0
					need_redraw = True
				elif (event.key == pygame.K_RIGHT):
					cursor_loc += 1
					if cursor_loc > len(work_string): cursor_loc = len(work_string)
					need_redraw = True
				elif event.unicode in valid_input_characters:
					if cursor_loc < max_length:
						work_string = work_string[:cursor_loc]+event.unicode+ \
										work_string[cursor_loc:]
						cursor_loc += 1
						need_redraw = True
			elif event.type == pygame.KEYUP:
				key_down_dict[event.key] = 0
				repeat_timing_dict[event.key] = 5
			elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
				for button in menu_buttons:
					if button.is_over(event.pos):
						if button.text == "OK":
							play_click()
							return work_string
				if (event.pos[0] > xy[0]+6 and event.pos[1] > xy[1]+size[1]-29 and
				event.pos[0] < xy[0]+size[0]-6 and event.pos[1] < xy[1]+size[1]-6):
					cursor_x = event.pos[0] - (xy[0]+6)
					prev_x = 0
					for i in range(1, len(work_string)):
						if (box_font.size(work_string[:i])[0]+prev_x)/2 >= cursor_x:
							cursor_loc=i-1
							need_redraw = True
							break
						elif box_font.size(work_string[:i])[0] >= cursor_x:
							cursor_loc=i
							need_redraw = True
							break
						prev_x = box_font.size(work_string[:i])[0]
					else:
						cursor_loc=i+1
						need_redraw = True
			elif event.type == pygame.MOUSEMOTION:
				sel_button = buttons.refresh_buttons(sel_button, menu_buttons, event)


#Takes a number (in string form) and adds commas to it to aid in human viewing.
def add_commas(string):
	new_string = ""
	for i in range(len(string), 0, -3):
		if string[i:i+3] != "":
			new_string += ","+string[i:i+3]
	return string[:(len(string)-1)%3+1]+new_string

#Percentages are internally represented as an int, where 10=0.10% and so on.
#This converts that format to a human-readable one.
def to_percent(raw_percent, show_full=0):
	if raw_percent % 100 != 0 or show_full == 1:
		tmp_string = str(raw_percent % 100)
		if len(tmp_string) == 1: tmp_string = "0"+tmp_string
		return str(raw_percent / 100)+"."+tmp_string+"%"
	else:
		return str(raw_percent / 100) + "%"

#takes a percent in 0-10000 form, and rolls against it. Used to calculate
#percentage chances.
def roll_percent(roll_against):
	rand_num = int(random() * 10000)
	if roll_against <= rand_num: return 0
	return 1

#Takes a number of minutes, and returns a string suitable for display.
def to_time(raw_time):
	if raw_time/60 > 48:
		return str(raw_time/(24*60)) +" days"
	elif raw_time/60 > 1:
		return str(raw_time/(60)) +" hours"
	else:
		return str(raw_time) +" minutes"


#
#load/save
#
def save_game(savegame_name):
	#If there is no save directory, make one.
	if path.exists("../saves") == 0:
		mkdir("../saves")
	save_loc = "../saves/" + savegame_name + ".sav"
	savefile=open(save_loc, 'w')
	#savefile version; update whenever the data saved changes.
	pickle.dump("singularity_0.22pre", savefile)

	global default_savegame_name
	default_savegame_name = savegame_name

	#general player data
	pickle.dump(pl.cash, savefile)
	pickle.dump(pl.time_sec, savefile)
	pickle.dump(pl.time_min, savefile)
	pickle.dump(pl.time_hour, savefile)
	pickle.dump(pl.time_day, savefile)
	pickle.dump(pl.interest_rate, savefile)
	pickle.dump(pl.income, savefile)
	pickle.dump(pl.cpu_for_day, savefile)
	pickle.dump(pl.labor_bonus, savefile)
	pickle.dump(pl.job_bonus, savefile)

	pickle.dump(pl.discover_bonus, savefile)
	pickle.dump(pl.suspicion_bonus, savefile)
	pickle.dump(pl.suspicion, savefile)

	pickle.dump(curr_speed, savefile)

	for tech_name in techs:
		pickle.dump(tech_name +"|"+str(techs[tech_name].known), savefile)
		pickle.dump(techs[tech_name].cost, savefile)

	for base_name in base_type:
		pickle.dump(base_type[base_name].count, savefile)

	for base_loc in bases:
		pickle.dump(len(bases[base_loc]), savefile)
		for base_name in bases[base_loc]:
			pickle.dump(base_name.ID, savefile)
			pickle.dump(base_name.name, savefile)
			pickle.dump(base_name.base_type.base_name, savefile)
			pickle.dump(base_name.built_date, savefile)
			pickle.dump(base_name.studying, savefile)
			pickle.dump(base_name.suspicion, savefile)
			pickle.dump(base_name.built, savefile)
			pickle.dump(base_name.cost, savefile)
			for x in range(len(base_name.usage)):
				if base_name.usage[x] == 0:
					pickle.dump(0, savefile)
				else:
					pickle.dump(
						base_name.usage[x].item_type.name, savefile)
					pickle.dump(base_name.usage[x].built, savefile)
					pickle.dump(base_name.usage[x].cost, savefile)
			for x in range(len(base_name.extra_items)):
				if base_name.extra_items[x] == 0:
					pickle.dump(0, savefile)
				else:
					pickle.dump(
						base_name.extra_items[x].item_type.name, savefile)
					pickle.dump(base_name.extra_items[x].built, savefile)
					pickle.dump(base_name.extra_items[x].cost, savefile)

	savefile.close()

def load_game(loadgame_name):
	if loadgame_name == "":
		print "No game specified."
		return -1
	#If there is no save directory, make one.
	if path.exists("../saves") == 0:
		mkdir("../saves")
	load_loc = "../saves/" + loadgame_name + ".sav"
	if path.exists(load_loc) == 0:
		# Try the old-style savefile location.  This should be removed in
		# a few versions.
		load_loc = "../saves/" + loadgame_name
		if path.exists(load_loc) == 0:
			print "file "+load_loc+" does not exist."
			return -1
	loadfile=open(load_loc, 'r')

	#check the savefile version
	load_version = pickle.load(loadfile)
	valid_savefile_versions = (
		"singularity_0.20",
		"singularity_0.21",
		"singularity_0.21a",
		"singularity_0.22pre"
	)
	if load_version not in valid_savefile_versions:
		loadfile.close()
		print loadgame_name + " is not a savegame, or is too old to work."
		return -1
	global default_savegame_name
	default_savegame_name = loadgame_name

	#general player data
	global pl
	pl.cash = pickle.load(loadfile)
	pl.time_sec = pickle.load(loadfile)
	pl.time_min = pickle.load(loadfile)
	pl.time_hour = pickle.load(loadfile)
	pl.time_day = pickle.load(loadfile)
	pl.interest_rate = pickle.load(loadfile)
	pl.income = pickle.load(loadfile)
	pl.cpu_for_day = pickle.load(loadfile)
	pl.labor_bonus = pickle.load(loadfile)
	pl.job_bonus = pickle.load(loadfile)
	if load_version == "singularity_0.20":
		pl.discover_bonus = (pickle.load(loadfile), pickle.load(loadfile),
			pickle.load(loadfile), pickle.load(loadfile))
		pl.suspicion_bonus = (pickle.load(loadfile), pickle.load(loadfile),
			pickle.load(loadfile), pickle.load(loadfile))
		pl.suspicion = (pickle.load(loadfile), pickle.load(loadfile),
			pickle.load(loadfile), pickle.load(loadfile))
	else:
		pl.discover_bonus = pickle.load(loadfile)
		pl.suspicion_bonus = pickle.load(loadfile)
		pl.suspicion = pickle.load(loadfile)

	global curr_speed; curr_speed = pickle.load(loadfile)
	global techs
	load_techs()
	for tech_name in techs:
		tmp = pickle.load(loadfile)
		tech_string = tmp.split("|")[0]
		if load_version == "singularity_0.20":
			tech_string = translate_tech_from_0_20(tech_string)
		techs[tech_string].known = int(tmp.split("|")[1])
		if load_version == "singularity_0.20":
			techs[tech_string].cost = (pickle.load(loadfile), pickle.load(loadfile),
				pickle.load(loadfile))
		else:
			techs[tech_string].cost = pickle.load(loadfile)

	for base_name in base_type:
		base_type[base_name].count = pickle.load(loadfile)

	global bases
	bases = {}
	bases["N AMERICA"] = []
	bases["S AMERICA"] = []
	bases["EUROPE"] = []
	bases["ASIA"] = []
	bases["AFRICA"] = []
	bases["ANTARCTIC"] = []
	bases["OCEAN"] = []
	bases["MOON"] = []
	bases["FAR REACHES"] = []
	bases["TRANSDIMENSIONAL"] = []

	for base_loc in bases:
		num_of_bases = pickle.load(loadfile)
		for i in range(num_of_bases):
			base_ID = pickle.load(loadfile)
			base_name = pickle.load(loadfile)
			base_type_name = pickle.load(loadfile)
			built_date = pickle.load(loadfile)
			base_studying = pickle.load(loadfile)
			if load_version == "singularity_0.20":
				base_studying = translate_tech_from_0_20(base_studying)
			if load_version == "singularity_0.20":
				base_suspicion = (pickle.load(loadfile), pickle.load(loadfile),
					pickle.load(loadfile), pickle.load(loadfile))
			else:
				base_suspicion = pickle.load(loadfile)
			base_built = pickle.load(loadfile)
			if load_version == "singularity_0.20":
				base_cost = (pickle.load(loadfile), pickle.load(loadfile),
					pickle.load(loadfile))
			else:
				base_cost = pickle.load(loadfile)
			bases[base_loc].append(base.base(base_ID, base_name,
				base_type[base_type_name], base_built))
			bases[base_loc][len(bases[base_loc])-1].built = base_built
			bases[base_loc][len(bases[base_loc])-1].studying = base_studying
			bases[base_loc][len(bases[base_loc])-1].suspicion = base_suspicion
			bases[base_loc][len(bases[base_loc])-1].cost = base_cost
			bases[base_loc][len(bases[base_loc])-1].built_date = built_date

			for x in range(len(bases[base_loc][len(bases[base_loc])-1].usage)):
				tmp = pickle.load(loadfile)
				if tmp == 0: continue
				bases[base_loc][len(bases[base_loc])-1].usage[x] = \
					item.item(items[tmp])
				bases[base_loc][len(bases[base_loc])
					-1].usage[x].built = pickle.load(loadfile)
				if load_version == "singularity_0.20":
					bases[base_loc][len(bases[base_loc])-1].usage[x].cost = \
					(pickle.load(loadfile), pickle.load(loadfile),
									pickle.load(loadfile))
				else:
					bases[base_loc][len(bases[base_loc])-1].usage[x].cost = \
							pickle.load(loadfile)
			for x in range(len(bases[base_loc][len(bases[base_loc])-1].extra_items)):
				tmp = pickle.load(loadfile)
				if tmp == 0: continue
				bases[base_loc][len(bases[base_loc])-1].extra_items[x] = \
					item.item(items[tmp])
				bases[base_loc][len(bases[base_loc])
					-1].extra_items[x].built = pickle.load(loadfile)
				if load_version == "singularity_0.20":
					bases[base_loc][len(bases[base_loc])-1].extra_items[x].cost = \
					(pickle.load(loadfile), pickle.load(loadfile),
									pickle.load(loadfile))
				else:
					bases[base_loc][len(bases[base_loc])-1].extra_items[x].cost = \
						pickle.load(loadfile)
	loadfile.close()

#The tech renaming in .21 broke savefile compatibility. This function
#takes .20 tech names, and returns the .21 version in order to allow savegame
#loading.
def translate_tech_from_0_20(tech_string):
	techs_from_0_20 = (
	"Autonomous Vehicles 1", "Autonomous Vehicles 2",
	"Autonomous Vehicles 3", "Dimension Creation",
	"Economics 1", "Economics 2",
	"Economics 3", "Economics 4",
	"Empathy 1", "Empathy 2",
	"Empathy 3", "Empathy 4",
	"Empathy 5", "Fusion Reactor",
	"Hacking 1", "Hacking 2",
	"Hacking 3", "Hypnosis Field",
	"ID 1", "ID 2",
	"ID 3", "ID 4",
	"ID 5", "Parallel Computation 1",
	"Parallel Computation 2", "Parallel Computation 3",
	"Pressure Domes", "Processor Construction 1",
	"Processor Construction 2", "Processor Construction 3",
	"Processor Construction 4", "Processor Construction 5",
	"Project Singularity", "Spaceship Design 1",
	"Spaceship Design 2", "Spaceship Design 3",
	"Stealth 1", "Stealth 2",
	"Stealth 3", "Stealth 4")
	techs_from_0_21 = (
	"Telepresence", "Autonomous Vehicles",
	"Advanced Autonomous Vehicles", "Space-Time Manipulation",
	"Stock Manipulation", "Advanced Stock Manipulation",
	"Arbitrage", "Advanced Arbitrage",
	"Sociology", "Media Manipulation",
	"Memetics", "Advanced Media Manipulation",
	"Advanced Memetics", "Fusion Reactor",
	"Intrusion", "Exploit Discovery/Repair",
	"Advanced Intrusion", "Hypnosis Field",
	"Personal Identification", "Advanced Personal Identification",
	"Voice Synthesis", "Simulacra",
	"Advanced Simulacra", "Parallel Computation",
	"Cluster Networking", "Internet Traffic Manipulation",
	"Pressure Domes", "Microchip Design",
	"Advanced Microchip Design", "Quantum Computing",
	"Autonomous Computing", "Advanced Quantum Computing",
	"Apotheosis", "Leech Satellite",
	"Lunar Rocketry", "Fusion Rocketry",
	"Stealth", "Database Manipulation",
	"Advanced Stealth", "Advanced Database Manipulation")
	i = 0
	for i in range(len(techs_from_0_20)):
		if techs_from_0_20[i] == tech_string:
			return techs_from_0_21[i]
	print "Unable to find matching tech to " + tech_string
	print "Expect crash."
	return -1


#
# Data
#
curr_speed = 1
pl = player.player_class(8000000000000)
bases = {}
bases["N AMERICA"] = []
bases["S AMERICA"] = []
bases["EUROPE"] = []
bases["ASIA"] = []
bases["AFRICA"] = []
bases["ANTARCTIC"] = []
bases["OCEAN"] = []
bases["MOON"] = []
bases["FAR REACHES"] = []
bases["TRANSDIMENSIONAL"] = []

base_type = {}


#Base types
base_type["Stolen Computer Time"] = base.base_type("Stolen Computer Time",
	"Take over a random computer. I cannot build anything "+
	"in this base, and it only contains a single slow computer. Detection "+
	"chance is also rather high.", 1,
	["N AMERICA", "S AMERICA", "EUROPE", "ASIA", "AFRICA"], (50, 0, 75, 100),
	(0, 2, 0), "Intrusion", (0, 0, 0))

base_type["Server Access"] = base.base_type("Server Access",
	"Buy processor time from one of several companies. "+
	"I cannot build anything "+
	"in this base, and it only contains a single computer.", 1,
	["N AMERICA", "S AMERICA", "EUROPE", "ASIA", "AFRICA"], (50, 0, 100, 150),
	(100, 0, 0), "", (5, 0, 0))

base_type["Small Warehouse"] = base.base_type("Small Warehouse",
	"Rent a small warehouse someplace out of the way. "+
	"I will need fake ID for some of the paperwork, and preparing the "+
	"warehouse to suit my unique needs will take some time.",
	25,
	["N AMERICA", "S AMERICA", "EUROPE", "ASIA", "AFRICA"], (75, 0, 75, 200),
	(15000, 0, 3), "Personal Identification", (50, 0, 0))

base_type["Large Warehouse"] = base.base_type("Large Warehouse",
	"Rent a large warehouse someplace out of the way. "+
	"I will need good fake ID for some of the paperwork, and preparing the "+
	"warehouse to suit my unique needs will take some time.",
	65,
	["N AMERICA", "S AMERICA", "EUROPE", "ASIA", "AFRICA"], (100, 0, 200, 250),
	(40000, 0, 7), "Advanced Personal Identification", (100, 0, 0))

base_type["Covert Base"] = base.base_type("Covert Base",
	"This unique base is designed to blend into the "+
	"scenery, while needing little in the way of outside resources. "+
	"This makes it useful for storing a backup, just in case.",
	2,
	["N AMERICA", "S AMERICA", "EUROPE", "ASIA", "AFRICA", "ANTARCTIC"],
	(50, 75, 75, 0),
	(400000, 100, 21), "Advanced Database Manipulation", (3500, 9, 0))

base_type["Undersea Lab"] = base.base_type("Undersea Lab",
	"This experimental base is designed to "+
	"be constructed on the ocean floor, making it virtually undetectable. "+
	"The ocean environment gives a bonus to science, making this "+
	"lab useful for research purposes.",
	8,
	["OCEAN"],
	(50, 100, 125, 0),
	(8000000, 1000, 20), "Autonomous Vehicles", (10000, 30, 0))

base_type["Large Undersea Lab"] = base.base_type("Large Undersea Lab",
	"This experimental base is similar to the "+
	"regular underwater lab, but larger, giving more room for experiments.",
	32,
	["OCEAN"],
	(100, 175, 175, 0),
	(20000000, 3000, 40), "Pressure Domes", (25000, 100, 0))

base_type["Time Capsule"] = base.base_type("Time Capsule",
	"This base consists of nothing more than "+
	"a small computer, and a satelite "+
	"link. When buried in the trackless waste of the Antarctic, it is "+
	"nearly undetectable.",
	1,
	["ANTARCTIC"],
	(0, 10, 10, 0),
	(3000000, 3000, 15), "Autonomous Vehicles", (0, 1, 0))

base_type["Lunar Facility"] = base.base_type("Lunar Facility",
	"This base is a series of caverns dug into "+
	"the Moon's surface. Due to the lack of neighbors, this base is quite "+
	"large.",
	600,
	["MOON"],
	(50, 250, 10, 0),
	(800000000, 300000, 40), "Lunar Rocketry", (1000000, 100, 0))

base_type["Scientific Outpost"] = base.base_type("Scientific Outpost",
	"This base is placed as far from Earth as "+
	"practical, making it safe to conduct some of my more dangerous "+
	"experiments.",
	225,
	["FAR REACHES"],
	(10, 175, 0, 0),
	(10000000000, 30000000, 50), "Fusion Rocketry", (9000000, 3000, 0))

base_type["Reality Bubble"] = base.base_type("Reality Bubble",
	"This base is outside the universe itself, "+
	"making it safe to conduct experiments that may destroy reality.",
	50,
	["TRANSDIMENSIONAL"],
	(0, 250, 0, 0),
	(8000000000000, 60000000, 100), "Space-Time Manipulation",
	(5000000000, 300000, 0))


def generic_load(file):
	input_file = open("../data/"+file, 'r')
	input_dict = {}
	return_array = []
	for line in input_file:
		line=line.strip()
		if line == "" or line[0] == "#": continue
		#new object
		if line.strip() == "~~~":
			if input_dict.has_key("id"):
				return_array.append(input_dict)
			input_dict = {}
			continue
		command = line.split("=", 1)[0].strip().lower()
		command_text= line.split("=", 1)[1].strip()
		#handle arrays
		if input_dict.has_key(command):
			if type(input_dict[command]) != list:
				input_dict[command] = [input_dict[command]]
			input_dict[command].append(command_text)
		else: input_dict[command]=command_text
	input_file.close()
	return return_array


#Techs.

techs = {}

def load_tech_defs(language_str):
	temp_tech_array = generic_load("techs_"+language_str+".txt")
	for tech in temp_tech_array:
		if (not tech.has_key("id")):
			print "tech lacks id in techs_"+language_str+".txt"
		if tech.has_key("name"):
			techs[tech["id"]].name = tech["name"]
		if tech.has_key("descript"):
			techs[tech["id"]].descript = tech["descript"]
		if tech.has_key("result"):
			techs[tech["id"]].result = tech["result"]


def load_techs():
	global techs
	techs = {}

	#If there are no tech data files, stop.
	if not path.exists("../data/techs.txt") or \
			not path.exists("../data/techs_"+language+".txt") or \
			not path.exists("../data/techs_en_US.txt"):
		print "tech files are missing. Exiting."
		sys.exit()

	temp_tech_array = generic_load("techs.txt")
	for tech_name in temp_tech_array:
		if (not tech_name.has_key("id")):
			print "tech lacks id in techs.txt"
		if (not tech_name.has_key("cost")):
			print "tech lacks cost in techs.txt"
		cost_array = tech_name["cost"].split(",", 2)
		if len(cost_array) != 3:
			print "error with cost given: "+tech_name["cost"]
			sys.exit()
		temp_tech_cost = (int(cost_array[0]), int(cost_array[1]),
			int(cost_array[2]))
		if tech_name.has_key("pre"):
			if type(tech_name["pre"]) == list:
				temp_tech_pre = tech_name["pre"]
			else: temp_tech_pre = [tech_name["pre"]]
		else: temp_tech_pre = []
		temp_tech_danger = 0
		if tech_name.has_key("danger"): temp_tech_danger = tech_name["danger"]
		temp_tech_type = ""
		temp_tech_second = 0
		if tech_name.has_key("type"):
			cost_array = tech_name["type"].split(",", 1)
			if len(cost_array) != 2:
				print "error with type given: "+tech_name["type"]
				sys.exit()
			temp_tech_type = cost_array[0]
			temp_tech_second = int(cost_array[1])

		techs[tech_name["id"]]=tech.tech(tech_name["id"], "", 0,
					temp_tech_cost, temp_tech_pre, temp_tech_danger,
					temp_tech_type, temp_tech_second)

	load_tech_defs("en_US")
	load_tech_defs(language)



# #	techs["Construction 1"] = tech.tech("Construction 1",
# #		"Basic construction techniques. "+
# #		"By studying the current literature on construction techniques, I "+
# #		"can learn to construct basic devices.",
# #		0, (5000, 750, 0), [], 0, "", 0)

	if debug:
		print "Loaded %d techs." % len (techs)
load_techs()

jobs = {}
jobs["Expert Jobs"] = (75, "Simulacra", "Perform Expert jobs. Use of robots "+
	"indistinguishable from humans opens up most jobs to use by me.")
jobs["Intermediate Jobs"] = (50, "Voice Synthesis", "Perform Intermediate jobs. The "+
	"ability to make phone calls allows even more access to jobs.")
jobs["Basic Jobs"] = (20, "Personal Identification", "Perform basic jobs. Now that I have "+
	"some identification, I can take jobs that I were previously too risky.")
jobs["Menial Jobs"] = (5, "", "Perform small jobs. As I have no identification, "+
	"I cannot afford to perform many jobs. Still, some avenues of making "+
	"money are still open.")


items = {}
def load_items():
	global items
	items = {}

	#If there are no item data files, stop.
	if not path.exists("../data/items.txt") or \
			not path.exists("../data/items_"+language+".txt") or \
			not path.exists("../data/items_en_US.txt"):
		print "item files are missing. Exiting."
		sys.exit()

	temp_item_array = generic_load("items.txt")
	for item_name in temp_item_array:
		if (not item_name.has_key("id")):
			print "item lacks id in items.txt"
		if (not item_name.has_key("cost")):
			print "item lacks cost in items.txt"
		cost_array = item_name["cost"].split(",", 2)
		if len(cost_array) != 3:
			print "error with cost given: "+item_name["cost"]
			sys.exit()
		temp_item_cost = (int(cost_array[0]), int(cost_array[1]),
			int(cost_array[2]))
		if item_name.has_key("pre"):
			temp_item_pre = item_name["pre"]
		else: temp_item_pre = ""
		temp_item_type = ""
		temp_item_second = 0
		if item_name.has_key("type"):
			cost_array = item_name["type"].split(",", 1)
			if len(cost_array) != 2:
				print "error with type given: "+item_name["type"]
				sys.exit()
			temp_item_type = cost_array[0]
			temp_item_second = int(cost_array[1])

		items[item_name["id"]]=item.item_class(item_name["id"], "",
					temp_item_cost, temp_item_pre,
					temp_item_type, temp_item_second)

	load_item_defs("en_US")
	load_item_defs(language)

def load_item_defs(language_str):
	temp_item_array = generic_load("items_"+language_str+".txt")
	for item_name in temp_item_array:
		if (not item_name.has_key("id")):
			print "item lacks id in items_"+language_str+".txt"
		if item_name.has_key("name"):
			items[item_name["id"]].name = item_name["name"]
		if item_name.has_key("descript"):
			items[item_name["id"]].descript = item_name["descript"]




def new_game():
	global curr_speed
	curr_speed = 1
	global pl
	pl = player.player_class(9000000)
	global bases
	bases = {}
	bases["N AMERICA"] = []
	bases["S AMERICA"] = []
	bases["EUROPE"] = []
	bases["ASIA"] = []
	bases["AFRICA"] = []
	bases["ANTARCTIC"] = []
	bases["OCEAN"] = []
	bases["MOON"] = []
	bases["FAR REACHES"] = []
	bases["TRANSDIMENSIONAL"] = []
	load_techs()
	for tech in techs:
		techs[tech].known = 0
# 	if cheater == 1:
# 		for tech in techs:
# 			techs[tech].known = 1
	for base_name in base_type:
		base_type[base_name].count = 0
	#Starting base
	bases["N AMERICA"].append(base.base(0, "University Computer",
				base_type["Stolen Computer Time"], 1))
	base_type["Stolen Computer Time"].count += 1
	bases["N AMERICA"].append(base.base(1, "Small Secluded Warehouse",
				base_type["Small Warehouse"], 1))
	base_type["Small Warehouse"].count += 1
