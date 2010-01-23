#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       sudoku.py
#       
#       Copyright 2009 Diogo Nuno <prom@diogonuno.com>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

sudoku_version = "0.2.1"
last_update = "10 Oct/2009"

import curses
import random
from random import shuffle

def InitCurses():
	'''Curses related stuff'''
	global screen
	screen = curses.initscr()
	curses.noecho()
	curses.start_color()
	curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
	curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
	curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_RED)
	curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)
	curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)
	screen.keypad(1)

# Screen information message position
info_x = 0
info_y = 1

def ScreenInfo(info_msg, info_color):
	'''Prints an information message in the position given up there'''
	last_pos = curses.getsyx()
	screen.move(info_x,info_y)
	screen.addstr("%s" % info_msg , curses.color_pair(info_color) | curses.A_BOLD)
	screen.move(last_pos[0],last_pos[1])

def Quit():
	'''Quiiiiiiiit!!!'''
	curses.endwin()
	quit()

class MoveCursor:
	'''
	An object to move the cursor with rules 
	Usage: MoveCursor(initial x position, initial y position, move left jump size, move right jump size, go up jump size, go down jump size, up limit size, down limit size, left limit size, right limit size) 
	'''
	def __init__(self,initial_x,initial_y,left,right,up,down,x_up_max,x_down_max,y_left_max,y_right_max):
		self.x = initial_x
		self.y = initial_y
		self.initial_x = initial_x
		self.initial_y = initial_x
		self.move_left = left
		self.move_right = right
		self.move_up = up
		self.move_down = down
		self.x_up_max = x_up_max
		self.y_left_max = y_left_max
		self.x_down_max = x_down_max
		self.y_right_max = y_right_max
	
	def MoveLeft(self):
		self.y = self.y-self.move_left
		if self.y < self.y_left_max:
			self.y = self.y_right_max

	def MoveRight(self):
		self.y = self.y+self.move_right
		if self.y > self.y_right_max:
			self.y = self.y_left_max

	def MoveUp(self):
		self.x = self.x-self.move_up
		if self.x < self.x_up_max:
			self.x = self.x_down_max

	def MoveDown(self):
		self.x = self.x+self.move_down
		if self.x > self.x_down_max:
			self.x = self.x_up_max
		
	def MoveInitial(self):
		self.x = self.initial_x
		self.y = self.initial_x

	def MoveActual(self):
		screen.move(self.x,self.y)
		
	def Move(self,option):
		if option == 'left':
			self.MoveLeft()
		elif option == 'right':
			self.MoveRight()
		elif option == 'up':
			self.MoveUp()
		elif option == 'down':
			self.MoveDown()
		elif option == 'initial':
			self.MoveInitial()
		elif option == 'actual':
			self.MoveActual()
		else:
			Quit()
	
	def get_x(self):
		'''Return X position'''
		return self.x
		
	def get_y(self):
		'''Return Y position'''
		return self.y

def About():
	'''About Sudoku'''	
	screen.clear()
	screen.move(0,0)
	screen.addstr(" Sudoku \n\n", curses.color_pair(3))
	screen.addstr(" Coded in 2009/08/28, a strange day for humanity\n");
	screen.addstr(" Version %s ( last update: %s )\n\n" % (sudoku_version,last_update));
	screen.addstr(" Made by Diogo Nuno\n Visit")
	screen.addstr(" http://www.diogonuno.com\n\n ", curses.color_pair(1))
	event = screen.getch()

def Help():
	'''Help me dear Sudoku'''	
	screen.clear()
	screen.move(0,0)
	screen.addstr(" Sudoku \n\n", curses.color_pair(3))
	screen.addstr(" Write numbers from 1 to 9 without using the same number in horizontal,\n vertical or square.\n")
	screen.addstr(" Use \"S\" in game to solve the game.\n")
	screen.addstr(" Use \"Q\" in game to quit.\n\n ")
	event = screen.getch()

class Number:
	'''Object number'''		
	def __init__(self, suit):
		self.suit = suit
		self.state = 0

	def setLock(self):
		'''Set locked on or not'''
		if self.state == 0:
			self.state = 1
		else:
			self.state = 0	

	def getState(self):
		'''Return if it is locked or not'''
		return self.state
		
	def getNumber(self):
		'''Return the number'''
		return self.suit

	def printNumber(self):
		'''Print the number'''
		if self.getState() == 1:
			screen.addstr(" %s " % self.getNumber(), curses.color_pair(4))
		elif self.getState() == 0:
			screen.addstr(" %s " % self.getNumber(), curses.color_pair(1))		

class Board():
	'''The game board'''
	def __init__(self,y,x):
		self.Board = [] # create the Board
		self.Board_x = x # lines
		self.Board_y = y # columns
		for i in range(y): # create the Board columns
			self.Board.append([])

class GameBoard(Board):
	'''The game board'''
	def __init__(self,y,x):
		Board.__init__(self,y,x)
		self.Number = Number(0)
		self.Fill()

	def Fill(self):
		'''Fill the board with random numbers so we can create random Sudoku'''
		for y in range(0,self.Board_y): # first we fill the board with 0's
			for x in range(0,self.Board_x):
				self.Board[y].append(Number(0))
		list1to9 = [] # create a list with numbers from 1 to 9 
		for i in range(0,9):
			list1to9.append(i+1)
		shuffle(list1to9)
		id = 0
		for y in range(0,3): 
			for x in range(0,3):
				self.Board[y][x] = Number(list1to9[id]) # put the numbers in the board 
				self.Board[y][x].setLock()
				id+=1
		shuffle(list1to9)
		id = 0
		for y in range(3,6): 
			for x in range(3,6):
				self.Board[y][x] = Number(list1to9[id]) # put more numbers in the board so we can create more random sudoku games
				self.Board[y][x].setLock()
				id+=1
		if self.Solve(0,0,True): # Genarate a solved sudoku with locked numbers
			for i in range(0,100): # a noob way of removing random numbers :P removes 100 times
				self.Board[random.randint(0, 8)][random.randint(0, 8)] = Number(0)
			
	def Print(self):
		'''Method to print our game board'''
		screen.addstr("\n\n"); # get a space for the information message 
		screen.addstr(" -------------------------------\n", curses.color_pair(5) | curses.A_BOLD) 
		for x in range(0,self.Board_x):
			screen.addstr(" |", curses.color_pair(5) | curses.A_BOLD)
			for y in range(0,self.Board_y):
				if self.Board[x][y].getNumber() != 0:
					self.Board[x][y].printNumber()
				else:
					screen.addstr("   ")
				if y == 2 or y == 5:
					screen.addstr("|", curses.color_pair(5) | curses.A_BOLD)
			screen.addstr("|\n", curses.color_pair(5) | curses.A_BOLD)
			if x == 2 or x == 5:
				screen.addstr(" -------------------------------\n", curses.color_pair(5) | curses.A_BOLD) 
		screen.addstr(" -------------------------------\n", curses.color_pair(5) | curses.A_BOLD) 

	def Solve(self,i,j,lock):
		'''Solve a Sudoku game'''
		if i == 9:
			i = 0
			j+=1
			if j == 9:
				return True
		if self.Board[i][j].getNumber() != 0:
			return self.Solve(i+1,j,lock)
		for number in range(1,10):
			if self.CheckNumber(i,j,number):
				self.setNumber(i,j,number,lock)
				if self.Solve(i+1,j,lock):
					return True
		self.setNumber(i,j,0,lock)
		return False

	def CheckNumber(self, i, j, number):
		'''If the number is ok return True'''
		for y in range(0,9): # check the column
			if number == self.Board[i][y].getNumber():
				return False
		for x in range(0,9): # check the row
			if number == self.Board[x][j].getNumber():
				return False
		checkRow = (i / 3)*3
		checkColumn = (j / 3)*3
		for x in range(0,3): # check the square
			for y in range(0,3):
				if number == self.Board[checkRow+x][checkColumn+y].getNumber():
					return False
		return True

	def setNumber(self, x, y, number, state):
		'''Set the desired number and lock it if True'''
		self.Board[x][y] = Number(number)
		if state:
			self.Board[x][y].setLock()

	def Play(self,x,y, number):
		'''The play method :)'''
		if self.Board[x][y].getNumber() == 0 or self.Board[x][y].getState() == 0:
			if self.CheckNumber(x,y,number) == True:
				self.setNumber(x,y,number,False)
			else:
				ScreenInfo("Bad number :)",2)
				screen.getch()				
		else:
			ScreenInfo("Can't play here!",2)
			screen.getch()

	def SomebodyWonPopcorn(self):
		'''Method to check if somebody has won and give its deserved price (not)'''
		calc=0
		for x in range(0,9):
			for y in range(0,9):
				calc += self.Board[x][y].getNumber()
		if calc == 45*9:
			return True
		return False

class Table:
	'''Table where we play. The board is in the table and the players are sitting right next to it :)'''	
	def __init__(self):
		self.Board = GameBoard(9,9)
		self.Cursor = MoveCursor(3,3,3,3,1,1,3,13,3,29) # give the rules to MoveCursor Object
		self.ChosenColumn = 0 # my chosen column
		self.ChosenRow = 0 # my chosen row
		self.Think() # The main
		
	def ChosenRowColumn(self, row, column):
		'''A method to get the right Row and Column to put the number and control the jump the cursor have to do in the game'''
		self.ChosenRow = row
		self.ChosenColumn = column		
		if self.ChosenRow < 0:
			self.ChosenRow = 8
		elif self.ChosenRow > 8:
			self.ChosenRow = 0
		elif self.ChosenColumn < 0:
			self.ChosenColumn = 8
		elif self.ChosenColumn > 8:
			self.ChosenColumn = 0
			
	def ForceBorderJump(self, keypress):
		'''Force the jump in the border when moving the cursor'''
		if keypress == 'right':
			if self.Cursor.get_y() == 12 or self.Cursor.get_y() == 22:
				self.Cursor.y = self.Cursor.get_y()+1
		elif keypress == 'left':
			if self.Cursor.get_y() == 10 or self.Cursor.get_y() == 20:
				self.Cursor.y = self.Cursor.get_y()-1
		elif keypress == 'up':
			if self.Cursor.get_x() == 6 or self.Cursor.get_x() == 10:
				self.Cursor.x = self.Cursor.get_x()-1
		elif keypress == 'down':
			if self.Cursor.get_x() == 6 or self.Cursor.get_x() == 10:
				self.Cursor.x = self.Cursor.get_x()+1

	def Think(self):
		'''Method where we read the keyboard keys and think in the game :P'''
		list = [ ] # create a list with numbers from 9 to 1. We will get the index from the event. example: 57-49=8, but the 8 number is the number 1 so we reverse the list so the index is correct :)
		for i in range (1,10):
			list.append(i)
		list.reverse()
		while True:
			screen.clear()
			self.Board.Print()
			if self.Board.SomebodyWonPopcorn(): # checks if he won :P
				ScreenInfo("YOU WIIIIIIIIN!!! :)",2)
				screen.getch()
				break
			self.Cursor.Move('actual')
			event = screen.getch()
			if event == ord("q"): 
				break
			elif event == curses.KEY_LEFT:
				self.Cursor.Move('left')
				self.ChosenRowColumn(self.ChosenRow,self.ChosenColumn-1)
				self.ForceBorderJump('left')
			elif event == curses.KEY_RIGHT:
				self.Cursor.Move('right')
				self.ChosenRowColumn(self.ChosenRow,self.ChosenColumn+1)
				self.ForceBorderJump('right')
			elif event == curses.KEY_UP:
				self.Cursor.Move('up')
				self.ChosenRowColumn(self.ChosenRow-1,self.ChosenColumn)
				self.ForceBorderJump('up')
			elif event == curses.KEY_DOWN:
				self.Cursor.Move('down')
				self.ChosenRowColumn(self.ChosenRow+1,self.ChosenColumn)
				self.ForceBorderJump('down')
			elif event >= 49 and event <= 57: # from 1 to 9
				self.Board.Play(self.ChosenRow,self.ChosenColumn,list[57-event]) # list[57-event] is the right number from the keyboard
			elif event == ord("s"): # S key
				self.Board.Solve(0,0,False)


class Menu:
	''''Where everything begins, the Menu (main too)'''	
	def __init__(self):
		self.Cursor = MoveCursor(2,0,0,0,1,1,2,5,0,0) # give the rules to MoveCursor Object
		self.main()

	def henshin_a_gogo_baby(self):
		'''A name inspired in Viewtiful Joe game, lol. It checks the cursor position and HENSHIN A GOGO BABY'''
		if self.Cursor.get_x() == 2:
			gogo = Table()
		elif self.Cursor.get_x() == 3:
			Help()
		elif self.Cursor.get_x() == 4:
			About()
		elif self.Cursor.get_x() == 5:
			Quit()
	
	def main(self):
		'''The main :|'''
		while True:
			screen.clear()
			screen.addstr(" Sudoku \n\n", curses.color_pair(3))
			screen.addstr("  Play\n")
			screen.addstr("  Help\n")
			screen.addstr("  About\n")
			screen.addstr("  Quit\n")
			self.Cursor.Move('actual')
			event = screen.getch()
			if event == ord("q"): 
				Quit()
			elif event == curses.KEY_UP:
				self.Cursor.Move('up')
			elif event == curses.KEY_DOWN:
				self.Cursor.Move('down')
			elif event == 10:
				self.henshin_a_gogo_baby()

if __name__ == '__main__': 
	try:
		InitCurses()
		run_for_your_life = Menu() # The menu
	except:
		Quit()
else:
	print "Sudoku - ??"
