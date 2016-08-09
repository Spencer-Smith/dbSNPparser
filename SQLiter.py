#Makes the SQLite database from 

import database
import databasemaker

class SQLiter:

	def __init__(self):
		self.dbName = "SNP.db"
		self.directory = "parsed\\"

	def SetUpDatabase(self, path):
		self.database = database.Database()
		self.dbName = path + self.dbName
		self.database.Connect(self.dbName)

	def Main(self):
		self.SetUpDatabase("")
		dbm = databasemaker.DatabaseMaker(self.database, self.directory)
		dbm.Main()
		self.database.Disconnect()
		self.database = database.Database()
		self.database.Connect(self.dbName)
		self.Unity()
		self.Minor()
		self.Variance()
		#self.CleanUp()

	def Unity(self):
		command = "CREATE TABLE fulltable as SELECT snpcontiglocusid.snp_id, prot_acc, aa_pos,"
		command += " function, residue, freq, eas, eur, afr, amr, sas FROM (snpcontiglocusid INNER"
		command += " JOIN allele ON allele.allele = snpcontiglocusid.allele INNER JOIN snpsubsnp"
		command += "link ON snpsubsnplink.snp_id = snpcontiglocusid.snp_id INNER JOIN allelefreq"
		command += "bysspop ON (allelefreqbysspop.subsnp_id = snpsubsnplink.subsnp_id AND allele"
		command += "freqbysspop.allele_id = allele.allele_id) INNER JOIN snpallelefreq ON (snpsub"
		command += "snplink.snp_id = snpallelefreq.snp_id AND allelefreqbysspop.allele_id = snp"
		command += "allelefreq.allele_id))"

		self.database.ExecuteCommand(command)
		self.database.Commit()

	def Minor(self):
		command = "CREATE TABLE minoralleles as SELECT * FROM fulltable "
		command += "WHERE freq BETWEEN .01 AND .5 "
		self.database.ExecuteCommand(command)

	def Variance(self):
		command = "CREATE TABLE minor01var05 as SELECT * FROM minoralleles "
		command += "WHERE (max(eas, eur, afr, amr, sas) - min(eas, eur, afr, amr, sas)) >= .05"
		self.database.ExecuteCommand(command)

	def CleanUp(self):
		command = "DROP TABLE allele"
		self.database.ExecuteCommand(command)
		command = "DROP TABLE allelefreqbysspop"
		self.database.ExecuteCommand(command)
		command = "DROP TABLE snpallelefreq"
		self.database.ExecuteCommand(command)
		command = "DROP TABLE snpcontiglocusid"
		self.database.ExecuteCommand(command)
		command = "DROP TABLE snpsubsnplink"
		self.database.ExecuteCommand(command)

if __name__ == "__main__":
	amigo = SQLiter()
	amigo.Main()