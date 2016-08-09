#A class to load the parsed, tab-delimited dbSNP files into a database

import database

class DatabaseMaker:

	def __init__(self, db, directory):
		self.database = db
		self.Directory = directory

	def Main(self):
		#Here we explicitly name each of our tables and pass that name into
		# the MakeTable method. We also create a list of types which will
		# indicate to the database what type that field should be. Info for
		# types comes from dbSNP table dictionary, found here:
			# http://www.ncbi.nlm.nih.gov/projects/SNP/snp_db_list_table.cgi
		types = ["integer", "varchar(255)", "integer"]
		self.MakeTable("Allele", types)
		types = ["integer", "integer", "real", "real", "real", "real", "real"]
		self.MakeTable("AlleleFreqBySsPop", types)
		types = ["integer", "integer", "real"]
		self.MakeTable("SNPAlleleFreq", types)
		types = ["integer", "varchar(50)", "varchar(15)", "smallint", "varchar(25)", "varchar(5)", "integer"]
		self.MakeTable("SNPContigLocusId", types)
		types = ["integer", "integer"]
		self.MakeTable("SNPSubSNPLink", types)
		types = ["varchar(50)", "varchar(50)", "varchar(50)"]
		self.MakeTable("AccessionMap", types)

		self.database.Commit()

	def MakeTable(self, TableName, types):
		path = self.Directory + TableName + ".Parsed.bcp"
		Handle = open(path, 'r')
		header = Handle.readline()

		#Break up the header to get the name for each field in the table
		fields = []
		dice = header.strip().split()
		for d in dice:
			fields.append(d)

		self.database.CreateTable(TableName, fields, types)

		#Each line is parsed for its info to be inserted into the table
		for line in Handle:
			values = line.strip().split("\t")
			self.database.InsertRow(TableName, values)

		Handle.close()
