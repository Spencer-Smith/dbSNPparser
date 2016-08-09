import sqlite3

class Database:

	def __init__(self):
		#I know I don't have to initialize variables, but it helps me keep track of them
		self.connection = ""
		self.dbpath = ""
		self.connected = False

	def is_number(self, string):
	    try:
	        float(string)
	        return True
	    except ValueError:
	        return False

	def GetDatabasePath(self):
		return self.dbpath

	def IsConnected(self):
		return self.connected
		
	def Connect(self, path):
		#Establishes the connection to the database, checking that appropriate flags have
		# been set. Returns "False" if the path variable does not existor if a connection 
		# already exists
		if self.connected:
			return False
		self.dbpath = path
		self.connection = sqlite3.connect(self.dbpath)
		self.connected = True
		return True

	def Reconnect(self):
		if self.connected:
			return False
		self.connection = sqlite3.connect(self.dbpath)
		self.connected = True
		return True
		
	def Disconnect(self):
		#Disconnects from the database, first checking that it's connected to a database. 
		# Returns "False" if not connected to a database
		if self.connected:
			self.connection.commit()
			self.connection.close()
			self.connected = False
			self.dbpath = ""
			return True
		else:
			return False

	def Commit(self):
		#Forces commitment
		self.connection.commit()

	def QueryDatabase(self, Query):
		#Queries the database and returns the result
		if self.connected:
			cursor = self.connection.execute(Query)
			return cursor

	def ExecuteCommand(self, command):
		if self.connected:
			self.connection.execute(command)

	def CreateTable(self, TableName, TableFields, TableTypes):
		command = "CREATE TABLE " + TableName + "\n("

		i = 0
		for properT in TableFields:
			command += properT + "\t" + TableTypes[i] + "," + "\n"
			i += 1

		command = command[:-2]
		command += ");"

		self.connection.execute(command)
		self.connection.commit()

	def InsertRow(self, TableName, RowValues):
		command = "INSERT INTO " + TableName + " VALUES ("

		for value in RowValues:
			if self.is_number(value):
				command += value + ","
			else:
				command += "'" + value + "',"				
		command = command[:-1] 
		command += ")"

		self.connection.execute(command)