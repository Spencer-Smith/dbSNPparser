#The function of this Python script is to parse down the .bcp files downloaded from dbSNP which
# are relevant to the Universal Clincal Assay project. The main method uses the following steps
# to cut down each file:
    # 1. Filter AlleleFreqBySsPop.bcp by pop_ids using Cut method
    # 2. Condense the result of (1) using the Juicer script
    # 3. Create a dictionary of SubSNP_IDs found in the result of (2)
    # 4. Filter SNPSubSNPLink.bcp using the dictionary from (3)
    # 5. Use FunctionFilter script to cut down b#_SNPContigLocusID_#.bcp
    # 6. Create a dictionary of SNP_IDs using the result of (4)
    # 7. Filter result of (5) using dictionary from (6)
    # 8. Create a dictionary of SNP_IDs using the result of (7)
    # 9. Filter result of (4) using dictionary from (8)
    # 10. Create a dictionary of SubSNP_IDs using the result of (9)
    # 11. Filter result of (2) using dictionary from (10)
    # 12. Create a dictionary of SNP_IDs using the restult of (9)
    # 13. Filter SNPAlleleFrequency_TGP.bcp using dictionary from (12)
    # 14. Create a dictionary of Allele_IDs using result of (13)
    # 15. Filter Allele.bcp using dictionary from (14)

import os
import sys
import getopt
import juicer
import functionfilter

class Carnicero:

    def __init__(self):
        self.ParseCommandLine(sys.argv[1:])
        self.SetFileNames()

    def SetFileNames(self):
        self.FreqByPopPath = self.Dir + "AlleleFreqBySsPop.bcp"
        self.FreqByPopHalfPath = "intermediates\FBP.half.bcp"
        self.FreqByPopCondensedPath = "intermediates\FBP.cond.bcp"
        self.FreqByPopOutPath = self.Out + "AlleleFreqBySsPop.Parsed.bcp"

        self.SNPSubSNPPath = self.Dir + "SNPSubSNPLink.bcp"
        self.SNPSubSNPHalfPath = "intermediates\SSS.half.bcp"
        self.SNPSubSNPOutPath = self.Out + "SNPSubSNPLink.Parsed.bcp"

        #THIS FILENAME MAY CHANGE WITH LATER BUILDS FROM dbSNP
        self.ContigPath = self.Dir + "b147_SNPContigLocusId_107.bcp"
        self.ContigHalfPath = "intermediates\Contig.half.bcp"
        self.ContigOutPath = self.Out + "SNPContigLocusId.Parsed.bcp"

        self.AlleleFreqPath = self.Dir + "SNPAlleleFreq_TGP.bcp"
        self.AlleleFreqOutPath = self.Out + "SNPAlleleFreq.Parsed.bcp"

        self.AllelePath = self.Dir + "Allele.bcp"
        self.AlleleOutPath = self.Out + "Allele.Parsed.bcp"

    def FirstFilterFreqPop(self):
        ## 1
        #From file Populations.1000GenomeOnly.bcp, we know the pop_ids we are interested in
        AcceptablePopulations = {"16651":1,"16652":1,"16653":1,"16654":1,"16655":1}
        #Knowledge of necessary columns comes from dbSNP's documentation. Link:
        # http://www.ncbi.nlm.nih.gov/SNP/snp_db_table_description.cgi?t=AlleleFreqBySsPop
            #[0] is subsnp_id, an id assigned to each submitted SNP by dbSNP
            #[1] is pop_id, which matches up with a population in the Population table
            #[2] is allele_id, which matches up with an allele in the Allele table
            #[5] is freq, the allele frequency 
        columns = [0,1,2,5]
        header = "SubSNP_ID\tPop_ID\tAllele_ID\tFreq\n"
        # [1] is the column we will filter by, as it contains the pop_ids
        self.Cut(self.FreqByPopPath,self.FreqByPopHalfPath, columns, AcceptablePopulations, 1, header)

        ## 2
        juice = juicer.Juicer(self.FreqByPopHalfPath, self.FreqByPopCondensedPath)
        juice.Main()

    def FirstFilterSNPSubSNP(self):
        ## 3
        AcceptableSubSNPs = self.Dictator(self.FreqByPopCondensedPath, 0)

        ## 4
        #Knowledge of necessary columns comes from dbSNP's documentation. Link:
        # http://www.ncbi.nlm.nih.gov/SNP/snp_db_table_description.cgi?t=SNPSubSNPLink
            #[0] is subsnp_id, an id assigned to each submitted SNP by dbSNP
            #[1] is snp_id, an id assigned by dbSNP to unique SNPs
        columns = [0,1]
        header = "SubSNP_ID\tSNP_ID\n"
        # Filter by [0], contains subsnp_ids
        self.Cut(self.SNPSubSNPPath, self.SNPSubSNPHalfPath, columns, AcceptableSubSNPs, 0, header)

    def FilterContig(self):
        ## 5
        #This script is used to reduce the SNPContigLocusID table to only include entries whose
        # minor alleles have a significant change in function
        funfil = functionfilter.FunctionFilter(self.ContigPath, self.ContigHalfPath)
        funfil.Main()

        ## 6
        AcceptableSNPs = self.Dictator(self.SNPSubSNPHalfPath,1)

        ## 7
        #Because we've already reduced the columns, we'll keep all 10 of them
        columns = [0,1,2,3,4,5,6]
        self.Cut(self.ContigHalfPath, self.ContigOutPath, columns, AcceptableSNPs, 0, "")

    def SecondFilterSNPSubSNP(self):
        ## 8
        AcceptableSNPs = self.Dictator(self.ContigOutPath, 0)

        ## 9
        #Keep both columns
        columns = [0,1]
        self.Cut(self.SNPSubSNPHalfPath, self.SNPSubSNPOutPath, columns, AcceptableSNPs, 1, "")

    def SecondFilterFreqPop(self):
        ## 10
        AcceptableSubSNPs = self.Dictator(self.SNPSubSNPOutPath, 0)

        ## 11
        #Keep all the columns
        columns = [0,1,2,3,4,5,6]
        self.Cut(self.FreqByPopCondensedPath, self.FreqByPopOutPath, columns, AcceptableSubSNPs, 0, "")

    def FilterAlleleFreq(self):
        ## 12
        AcceptableSNPs = self.Dictator(self.SNPSubSNPOutPath, 1)
        
        ## 13
        #Knowledge of necessary columns comes from dbSNP's documentation. Link:
        # http://www.ncbi.nlm.nih.gov/SNP/snp_db_table_description.cgi?t=SNPAlleleFreq
        # NOTE!: However, that information actually applies to a slightly different table.
        # There was no way to learn this other than look at the actual file, which shows that
        # frequency is in the third rather than fourth column
            #[0] is snp_id, an id assigned to each submitted SNP by dbSNP
            #[1] is allele_id, which matches up with an allele in the Allele table
            #[2] is freq, the allele frequency
        columns = [0,1,2]
        header = "SNP_ID\tAllele_ID\tFreq\n"
        self.Cut(self.AlleleFreqPath, self.AlleleFreqOutPath, columns, AcceptableSNPs, 0, header)

    def FilterAllele(self):
        ## 14
        AcceptableAlleles = self.Dictator(self.AlleleFreqOutPath, 1)

        ## 15
        #Knowledge of necessary columns comes from dbSNP's documentation. Link:
        # http://www.ncbi.nlm.nih.gov/SNP/snp_db_table_description.cgi?t=Allele
            #[0] is allele_id
            #[1] is allele, the actual nucleotides of the allele_id
        columns = [0,1,4]
        header = "Allele_ID\tAllele\tInverseID\n"
        self.Cut(self.AllelePath,self.AlleleOutPath, columns, AcceptableAlleles, 0, header)

    def Main(self):
        #This method goes through the specific parsing steps necessary to
        # reduce the files in an efficent manner, using the steps above
        #The steps have been broken into separate functions to reduce
        # the scope of dictionary objects

        self.FirstFilterFreqPop()
        self.FirstFilterSNPSubSNP()
        self.FilterContig()
        self.SecondFilterSNPSubSNP()
        self.SecondFilterFreqPop()
        self.FilterAlleleFreq()
        self.FilterAllele()
       
    def Dictator(self, path, col):
        #This method makes dictionaries from a specified column of a file
        Handle = open(path,'r')
        Handle.readline() #Ignore header
        toReturn = {}

        for line in Handle:
            Bits = line.strip().split()
            key = Bits[col]
            toReturn[key] = 1

        Handle.close()
        return toReturn

    def Cut(self, InPath, OutPath, columns, dictionary, FilterColumn, header):
        #Parses columns and filters rows based on given criteria
        Handle = open(InPath, 'r')
        OutHandle = open(OutPath, 'w')

        #Prints header if one has been passed, if not it will use the first line of
        # the file, assuming it already has a header
        if header == "":
            Header = Handle.readline()
        else:
            Header = header
        OutHandle.write(Header)

        counter = 0

        for line in Handle:
            #Added a counter so we know it's working
            counter +=1
            if counter % 1000000 ==0:
                print ("Progress: Read %s lines"%counter)

            Bits = line.strip().split()

            if len(Bits) - 1 < max(columns):
                #Avoids errors if the highest column index in columns can't be found
                continue

            #Here we filter out rows that don't fit our parameters (not in dictionary)
            if not Bits[FilterColumn] in dictionary:
                continue #Skip the rest of the loop and move to the next row

            #Here we build a new line using the columns we're interested in
            NewOutLine = ""
            for col in columns:
                NewOutLine += Bits[col] + "\t"
            NewOutLine = NewOutLine[:-1]
            NewOutLine += "\n"
            OutHandle.write(NewOutLine)
            
        Handle.close()
        OutHandle.close()

    def ParseCommandLine(self, Arguments):
        (Options, Args) = getopt.getopt(Arguments, "d:o:")
        OptionsSeen = {}
        for (Option, Value) in Options:
            OptionsSeen[Option] = 1
            if Option == "-d":
                if not os.path.exists(Value):
                    print ("  ERROR: could not find directory, %s"%Value)
                    sys.exit(1)
                self.Dir = Value
            if Option == "-o":
                if not os.path.exists(Value):
                    print ("  ERROR: could not find output directory, %s"%Value)
                    sys.exit(1)
                self.Out = Value
        if not "-d" in OptionsSeen.keys():
            self.Dir = "unparsed\\"
            self.Out = "parsed\\"

if __name__ == "__main__":
    eggo = Carnicero()
    eggo.Main()