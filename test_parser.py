#This class tests the Parser script

import unittest
import os
import Parser
import Juicer
import FunctionFilter

class ParserTestCase(unittest.TestCase):

	def setUp(self):
		self.parser = Parser.Parser()
		self.juicer = Juicer.Juicer("","")
		self.funfil = FunctionFilter.FunctionFilter("","")
		self.funfil.SetFunctionCodes()
		self.output = "TESTfiles\output.txt"

	def checkmywork(self, file1, file2):
		#This method just checks that two files are equivalent
		in1 = open(file1,'r')
		in2 = open(file2,'r')

		while True:
			line1 = in1.readline()
			line2 = in2.readline()
			if line1 != line2:
				in1.close()
				in2.close()
				return False

			if line1 == '' and line2 == '':
				break
		in1.close()
		in2.close()
		return True

	#The Dictator method makes a dictionary given a file a column of the file.
		# Prototype: Dictator(InputPath, TargetColumn)
	def test_make_dictionary_from_one_column_file(self):
		"""Can the dictator method make a dictionary from a one column file?"""
		expectedDictionary = {"this":1, "is":1, "a":1, "dictionary":1}
		path = "TESTfiles\TEST_one_column_file.txt"
		self.assertEqual(self.parser.Dictator(path,0), expectedDictionary)

	def test_make_dictionary_from_two_column_file(self):
		"""Can the dictator method make a dictionary from a two column file?"""
		expectedDictionary = {"this":1, "is":1, "a":1, "dictionary":1}
		path = "TESTfiles\TEST_two_column_file.txt"
		self.assertEqual(self.parser.Dictator(path,1), expectedDictionary)

	#The Carnicero method reads in a file, and parses out only the desired columns. Each row can 
		# have a column compared against a dictionary of acceptable values, excluding those rows
		# which do not meet the criteria. The remaining columns of each row are printed to an
		# output file. A passed header is passed, it will be output first to the output file, 
		# however if the Header argument is left as an empty string (""), then the first line of 
		# the input file will be considered a header and written to the output file
		# Prototype: Carnicero(InPath, OutPath, ColumnsToKeep, DictionaryOfAcceptableValues,
		# 							ColumnToChallengeDictionary, Header)

	def test_cut_one_column(self):
		"""Can the carnicero method keep all but one column?"""
		path = "TESTfiles\TEST_table.txt"
		columns = [0,1,3]
		dictionary = {"blue":1,"red":1,"orange":1,"black":1,"teal":1,"silver":1,"outofspace":1,"green":1,"purple":1}
		col = 3
		header = "number\tword\tcolor\n"
		self.parser.Carnicero(path,self.output,columns,dictionary,col,header)
		expected = "TESTfiles\expected_cut_one_column.txt"
		self.assertTrue(self.checkmywork(self.output, expected), msg="Output not equal to expected")

	def test_keep_one_column(self):
		"""Can the carnicero method keep only one column?"""
		path = "TESTfiles\TEST_table.txt"
		columns = [3]
		dictionary = {"blue":1,"red":1,"orange":1,"black":1,"teal":1,"silver":1,"outofspace":1,"green":1,"purple":1}
		col = 3
		header = "color\n"
		self.parser.Carnicero(path,self.output,columns,dictionary,col,header)
		expected = "TESTfiles\expected_keep_one_column.txt"
		self.assertTrue(self.checkmywork(self.output, expected), msg="Output not equal to expected")

	def test_limit_by_dictionary(self):
		"""Can the carnicero method remove rows with a value not pertaining to a dictionary?"""
		path = "TESTfiles\TEST_table.txt"
		columns = [0,1,2,3]
		dictionary = {"blue":1,"orange":1,"black":1,"outofspace":1,"green":1,"purple":1}
		col = 3
		header = "number\tword\tplace\tcolor\n"
		self.parser.Carnicero(path,self.output,columns,dictionary,col,header)
		expected = "TESTfiles\expected_limit_by_dictionary.txt"
		self.assertTrue(self.checkmywork(self.output, expected), msg="Output not equal to expected")

	def test_cut_two_columns_limit_by_dictionary(self):
		"""Can the carnicero method cut and limit at the same time?"""
		path = "TESTfiles\TEST_table.txt"
		columns = [1,2]
		dictionary = {"ephemeral":1,"zephyr":1,"cordial":1,"external":1}
		col = 1
		header = "word\tplace\n"
		self.parser.Carnicero(path,self.output,columns,dictionary,col,header)
		expected = "TESTfiles\expected_cut_two_columns_limit_by_dictionary.txt"
		self.assertTrue(self.checkmywork(self.output, expected), msg="Output not equal to expected")

	#The Juicer class uses it's ParseFile method to parse files. It stores the entries on a line,
		# in a buffer until the first column changes. It then calls CheckBuffer, which ensures
		# that at least one of the frequencies in the buffer has a minor allele frequency greater
		# than 1%, and then PrintBuffer. The buffer should contain ten lines, but is printed as
		# two lines by placing all frequencies the same population ID on the same line. NOTE: This
		# last operation does not depend on detecting the population ID, but instead attaches every
		# other line to a first or second line, then prints them.

	def test_buffer_all_MAF_greater_than_one(self):
		"""Can CheckBuffer pass a buffer where all MAF are greater than 1%?"""
		self.juicer.Buffer = [[".011" for i in range(4)],[".989" for j in range(4)]] * 5
		self.assertTrue(self.juicer.CheckBuffer())

	def test_buffer_one_MAF_greater_than_one(self):
		"""Can CheckBuffer pass a buffer where only one MAF is greater than 1%
			and the rest are less than 1%?"""
		self.juicer.Buffer = [[".009" for i in range(4)],[".991" for j in range(4)]] * 4
		self.juicer.Buffer += [".011" for i in range(4)],[".989" for j in range(4)]
		self.assertTrue(self.juicer.CheckBuffer())

	def test_buffer_all_MAF_less_than_one(self):
		"""Can CheckBuffer fail a buffer where all MAF are less than 1%?"""
		self.juicer.Buffer = [[".009" for i in range(4)],[".991" for j in range(4)]] * 5
		self.assertFalse(self.juicer.CheckBuffer())

	def test_buffer_MAF_equal_to_one(self):
		"""Can CheckBuffer fail a buffer where all MAF are equal to 1%? Or
			where one is equal and the rest are less than 1%? Can it pass
			when one or more are equal to one but another is greater?"""
		self.juicer.Buffer = [[".01" for i in range(4)],[".99" for j in range(4)]] * 5
		self.assertFalse(self.juicer.CheckBuffer(), msg="CheckBuffer should not pass when equal to 1%")

		self.juicer.Buffer = [[".009" for i in range(4)],[".991" for j in range(4)]] * 4
		self.juicer.Buffer += [".01" for i in range(4)],[".99" for j in range(4)]
		self.assertFalse(self.juicer.CheckBuffer(), msg="CheckBuffer should not pass when equal to 1%")

		self.juicer.Buffer = [[".01" for i in range(4)],[".99" for j in range(4)]] * 4
		self.juicer.Buffer += [".011" for i in range(4)],[".991" for j in range(4)]
		self.assertTrue(self.juicer.CheckBuffer())

		self.juicer.Buffer = [[".011" for i in range(4)],[".989" for j in range(4)]] * 4
		self.juicer.Buffer += [".01" for i in range(4)],[".99" for j in range(4)]
		self.assertTrue(self.juicer.CheckBuffer())

	def test_buffer_not_full(self):
		"""Will CheckBuffer fail if the buffer has missing information?"""
		self.juicer.Buffer = [[".011" for i in range(3)],[".989" for j in range(3)]] * 5
		self.assertFalse(self.juicer.CheckBuffer(), msg="Buffer not full, should return false")

	def test_juicer_write_buffer(self):
		"""Does WriteBuffer properly output the data from the buffer?"""
		self.juicer.Buffer = [["1","51","2","0.91"],["1","51","7","0.09"],["1","52","2","0.95"],
			["1","52","7","0.05"],["1","53","2","0.93"],["1","53","7","0.07"],["1","54","2","0.99"],
			["1","54","7","0.01"],["1","55","2","0.89"],["1","55","7","0.11"]]
		out = open(self.output, 'w')
		self.juicer.WriteBuffer(out)
		out.close()
		expected = "TESTfiles\expected_juicer_write_buffer.txt"
		self.assertTrue(self.checkmywork(self.output, expected), msg="Output not equal to expected")

	#The FunctionFilter class also has a ParseFile method, which also begins by storing lines in a
		# buffer to keep information for a single SNP together. When the data being read in no longer
		# pertains to the same SNP, the buffer is checked with a CheckBuffer method, which makes sure
		# that the function of the SNP is one that we're interested in. It then writes the buffer,
		# excluding columns that we're not interested in. SNPs with reversed mRNA orientation will
		# also have their alleles switched to the reverse compliment through the ReverseCompliment
		# method.

	def test_buffer_valid_codes(self):
		"""Will CheckBuffer pass all valid codes?"""
		self.funfil.Buffer = [["8" for i in range(25)] for j in range(2)]
		self.assertTrue(self.funfil.CheckBuffer(), msg="8 is a valid function code")
		self.funfil.Buffer = [["41" for i in range(25)] for j in range(2)]
		self.assertTrue(self.funfil.CheckBuffer(), msg="41 is a valid function code")
		self.funfil.Buffer = [["42" for i in range(25)] for j in range(2)]
		self.assertTrue(self.funfil.CheckBuffer(), msg="42 is a valid function code")
		self.funfil.Buffer = [["43" for i in range(25)] for j in range(2)]
		self.assertTrue(self.funfil.CheckBuffer(), msg="43 is a valid function code")
		self.funfil.Buffer = [["44" for i in range(25)] for j in range(2)]
		self.assertTrue(self.funfil.CheckBuffer(), msg="44 is a valid function code")
		self.funfil.Buffer = [["45" for i in range(25)] for j in range(2)]
		self.assertTrue(self.funfil.CheckBuffer(), msg="45 is a valid function code")

	def test_buffer_nonvalid_codes(self):
		"""Will CheckBuffer fail invalid codes?"""
		self.funfil.Buffer = [["3" for i in range(25)] for j in range(2)]
		self.assertFalse(self.funfil.CheckBuffer(), msg="3 is not a valid function code")
		self.funfil.Buffer = [["6" for i in range(25)] for j in range(2)]
		self.assertFalse(self.funfil.CheckBuffer(), msg="6 is not a valid function code")
		self.funfil.Buffer = [["9" for i in range(25)] for j in range(2)]
		self.assertFalse(self.funfil.CheckBuffer(), msg="9 is not a valid function code")
		self.funfil.Buffer = [["30" for i in range(25)] for j in range(2)]
		self.assertFalse(self.funfil.CheckBuffer(), msg="30 is not a valid function code")
		self.funfil.Buffer = [["53" for i in range(25)] for j in range(2)]
		self.assertFalse(self.funfil.CheckBuffer(), msg="53 is not a valid function code")
		self.funfil.Buffer = [["75" for i in range(25)] for j in range(2)]
		self.assertFalse(self.funfil.CheckBuffer(), msg="75 is not a valid function code")

	def test_buffer_nonsense_codes(self):
		"""Does CheckBuffer know what to do with input that is not codes at all?"""
		self.funfil.Buffer = [["-21" for i in range(25)] for j in range(2)]
		self.assertFalse(self.funfil.CheckBuffer(), msg="-21 isn't even a code at all")
		self.funfil.Buffer = [["over 9000" for i in range(25)] for j in range(2)]
		self.assertFalse(self.funfil.CheckBuffer(), msg="over 9000 isn't even a code at all")
		self.funfil.Buffer = [["A" for i in range(25)] for j in range(2)]
		self.assertFalse(self.funfil.CheckBuffer(), msg="A isn't even a code at all")
		self.funfil.Buffer = [["zenith" for i in range(25)] for j in range(2)]
		self.assertFalse(self.funfil.CheckBuffer(), msg="zenith isn't even a code at all")
		self.funfil.Buffer = [["...." for i in range(25)] for j in range(2)]
		self.assertFalse(self.funfil.CheckBuffer(), msg=".... isn't even a code at all")
		self.funfil.Buffer = [[";)" for i in range(25)] for j in range(2)]
		self.assertFalse(self.funfil.CheckBuffer(), msg=";) isn't even a code at all")
		self.funfil.Buffer = [["" for i in range(25)] for j in range(2)]
		self.assertFalse(self.funfil.CheckBuffer(), msg=" isn't even a code at all")

	def test_buffer_mixed_codes(self):
		"""Will CheckBuffer fail valid codes when invalid codes are present?"""
		self.funfil.Buffer = [["8" for i in range(25)],["3" for i in range(25)]]
		self.assertFalse(self.funfil.CheckBuffer(), msg="8 is a valid function code")

	def test_reverse_comp_single_nucleotides(self):
		"""Can ReverseCompliment return the compliment of a single nucleotide?"""
		nuc = "A"
		self.assertEqual(self.funfil.ReverseCompliment(nuc), "T")
		nuc = "C"
		self.assertEqual(self.funfil.ReverseCompliment(nuc), "G")
		nuc = "G"
		self.assertEqual(self.funfil.ReverseCompliment(nuc), "C")
		nuc = "T"
		self.assertEqual(self.funfil.ReverseCompliment(nuc), "A")

	def test_reverse_comp_long_sequences(self):
		"""Can ReverseCompliment make the reverse compliments of longer (3-9
			nucleotides) sequences?"""
		nuc = "CAT"
		self.assertEqual(self.funfil.ReverseCompliment(nuc), "ATG")
		nuc = "TAGAC"
		self.assertEqual(self.funfil.ReverseCompliment(nuc), "GTCTA")
		nuc = "ACCATAGGA"
		self.assertEqual(self.funfil.ReverseCompliment(nuc), "TCCTATGGT")

	def test_reverse_comp_hyphen(self):
		"""In the SNPContigLocusId table, hyphens("-") indicate the absense of
			an allele (e.g, in indel SNPs). Does ReverseCompliment correctly
			return a hyphen in response to a hyphen?"""
		hyphy = "-"
		self.assertEqual(self.funfil.ReverseCompliment(hyphy), hyphy)

	def test_reverse_comp_nonnucleotide_input(self):
		"""Does ReverseCompliment correctly return any character other than a
			nucleotide or a hyphen as an empty string ?"""
		notnuc = "M"
		self.assertEqual(self.funfil.ReverseCompliment(notnuc), "",
				msg="'M' is not a nucleotide")
		notnuc = "win"
		self.assertEqual(self.funfil.ReverseCompliment(notnuc), "",
			msg="No character of 'win' is a valid nucleotide")
		notnuc = "a"
		self.assertEqual(self.funfil.ReverseCompliment(notnuc), "",
			msg="Nucleotides must be capitalized to be considered valid")		
		notnuc = "?"
		self.assertEqual(self.funfil.ReverseCompliment(notnuc), "",
				msg="'?' is not a nucleotide")
		notnuc = ""
		self.assertEqual(self.funfil.ReverseCompliment(notnuc), "",
				msg="Empty string is not a nucleotide")

	def test_funfil_write_buffer(self):
		"""Does WriteBuffer write the correct columns to output?"""
		self.funfil.Buffer = [["8" for i in range(25)],["42" for i in range(25)]]
		self.funfil.Buffer[0][13] = "A"
		self.funfil.Buffer[1][13] = "G"
		self.funfil.Buffer[0][24] = self.funfil.Buffer[1][24] = "0"
		out = open(self.output, 'w')
		self.funfil.WriteBuffer(out)
		out.close()
		expected = "TESTfiles\expected_funfil_write_buffer.txt"
		self.assertTrue(self.checkmywork(self.output, expected), msg="Output not equal to expected")

	def test_funfil_write_buffer_reverse_comp(self):
		"""Does WriteBuffer call reverse compliment when necessary?"""
		self.funfil.Buffer = [["8" for i in range(25)],["42" for i in range(25)]]
		self.funfil.Buffer[0][13] = "A"
		self.funfil.Buffer[1][13] = "G"
		self.funfil.Buffer[0][24] = self.funfil.Buffer[1][24] = "1"
		out = open(self.output, 'w')
		self.funfil.WriteBuffer(out)
		out.close()
		expected = "TESTfiles\expected_funfil_write_buffer_reverse_comp.txt"
		self.assertTrue(self.checkmywork(self.output, expected), msg="Output not equal to expected")

if __name__ == '__main__':
    unittest.main()