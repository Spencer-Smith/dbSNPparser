***How to Parse your Database***

PART I: Parse Tables

#PREREQUISITES
-Python 3.5 installed on system

#PREPARATION
Before using the Parser script, do the following tables must be downloaded from dbSNP in a single directory on system:
Allele.bcp, AlleleFreqBySsPop.bcp, b#_SNPContigLocusId.bcp, SNPAlleleFrequency_TGP.bcp, and SNPSubSNPLink.bcp.
	-These files can be downloaded from the dbSNP FTP archive for humans:
		ftp://ftp.ncbi.nih.gov/snp/organisms/human_9606/database/organism_data/
	- ...except for the Allele.bcp table which can found in the shared data folder:
		ftp://ftp.ncbi.nih.gov/snp/database/shared_data/
The files are very large (some being several GB), downloading can take more than an hour.
	-The files, when downloaded, will be compressed (note the "*.gz" suffix). They can be decompressed with any 
	  file extraction program; e.g, 7-zip (http://www.7-zip.org/)

By default, Parser.py looks for the files in the included "unparsed" folder. It is recommended to put the extracted
tables in that folder.

#EXECUTION
If all 5 tables have been placed in the "unparsed" folder, then the whole parsing process can be done by simply double
-clicking the "Parser.py" script to open it with Python. Otherwise, it can be run on the commandline by navigating to
the script folder and using the command "(python) Parser.py".

Note that because of the size of the files, the execution of the script can take several (6-8) hours.

#COMMANDLINE OPTIONS
There are two optional commandline options:
1. "-d (directory)" indicates a directory other than "unparsed" where Parser.py can find the tables. Note that the 
	all tables must still be together in the same directory.
2. "-o (directory)" indicates a directory to output the finished, parsed tables. If the option is unused, the files 
	will be output to the included "parsed" folder.

#OUTPUT
The result of the parsing is 5 significantly downsized tables that will be output with the suffix "*.Parsed.bcp" 
into either the "parsed" folder, or the user-specified folder if the commandline option is used.


PART II: Make SQLite Database

#PREPARATION
All of the parsed files must be in the included "parsed" folder. Another table, "AccessionMap.Parsed.bcp" should 
already be in that folder.

#EXECUTION
The script can be run by double clicking to run with python or through the commandline.

#OUTPUT
The script outputs a database file called "SNP.db". SNP.db has a table for each of the parsed table files, as well as
a table as a result of the joining of the critical components of those tables, that table reduced to hold only minor
alleles, then another table reduced to SNPs with > 1% global frequency and >= 5% variation among populations. 