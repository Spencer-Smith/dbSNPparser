#Parses down bcp files downloaded from dbSNP, limiting it to useful data

import os
import sys
import getopt
import string
from collections import defaultdict

class FunctionFilter:

    def __init__(self,InPath,OutPath):
        self.InputFilePath = InPath
        self.OutFilePath = OutPath
        self.Compliments = {'A':'T', 'C':'G', 'G':'C', 'T':'A', '-':'-'}
        self.Compliments = defaultdict(lambda: "", self.Compliments)

    def Main(self):
        #Limit the file by filtering rows by function codes
        self.SetFunctionCodes()
        self.ParseFile(self.InputFilePath, self.OutFilePath)

    def SetFunctionCodes(self):
        #Adding relevant function codes to a dictionary. This information comes from the file 
        #SnpFunctionCode.bcp, found at: ftp://ftp.ncbi.nih.gov/snp/database/shared_data/
        self.FunctionCodes = {}
        self.FunctionCodes["8"] = 1 # reference
        self.FunctionCodes["41"] = 1 # stop gain, minor allele forms a stop codon, cutting protein short
        self.FunctionCodes["42"] = 1 # missense, minor allele changes the amino acid to another
        self.FunctionCodes["43"] = 1 # stop loss, minor allele changes a stop codon, increasing protein length
        self.FunctionCodes["44"] = 1 # frameshift, insertion or deletion of causing change in many amino acids
        self.FunctionCodes["45"] = 1 # cds-indel, insertion or deletion multiple of 3 bp, removes some amino
                                       # acids but the rest of the chain is unchanged

    def CreateHeader(self):
        #This knowledge came from dbSNP's documentation. Link:
        #	http://www.ncbi.nlm.nih.gov/SNP/snp_db_table_description.cgi?t=SNPContigLocusId
        returnString = "SNP_ID\tGene\tProt_Acc\tFxn_Class\tAllele\tResidue\tAA_Pos\n"
        return returnString

    def ReverseCompliment(self, nucleotides):
        revcom = ""
        for nucleotide in nucleotides:
            revcom = self.Compliments[nucleotide] + revcom
        return revcom

    def CheckBuffer(self):
        #Make sure at least all alleles in the buffer have a valid function code 
        for Bits in self.Buffer:
            if Bits[11] not in self.FunctionCodes:
                return False
        return True

    def WriteBuffer(self, OutHandle):
        #[0] is the snp_id
        #[6] is Gene, the name of the gene which codes the protein
        #[9] is Prot_Acc, the protein accession number on NCBI databases
        #[11] is Fxn_Class, the function (effect) of the minor allele
        #[13] is Allele, the mRNA allele of the SNP
        #[14] is Residue, the residue result of the allele
        #[15] is AA_Pos, the position of this amino acid on the protein
        #[24] is mRNA_orientation, which tells us if we need to find the
            # reverse compliment of the allele in [13]
        for Bits in self.Buffer:
            #If the mRNA_orientation is '1' (reverse), invert it.
            allele = Bits[13]
            if Bits[24] == '1':
                allele = self.ReverseCompliment(allele)

            OutLine = Bits[0] + "\t" + Bits[6] + "\t" + Bits[9] + "\t" + Bits[11]
            OutLine += "\t" + allele + "\t" + Bits[14] + "\t" + Bits[15] + "\n"
            OutHandle.write(OutLine)

    def ParseFile(self, InPath, OutPath):
        Handle = open(InPath, 'r')
        OutHandle = open(OutPath, 'w')
        Header = self.CreateHeader()
        OutHandle.write(Header)
        counter = 0
        currentID = ""

        #We use a buffer to check the function codes for all alleles before writing, so we can save 
        # and write the reference allele, even though it does not have a function in our dictionary
        self.Buffer = []

        for line in Handle:
            counter +=1
            if counter % 1000000 == 0 :
                print ("Progress: Read %s lines"%counter)
            Bits = line.strip().split()

            #This check is here because SNPs not associated with proteins have too few fields
            if len(Bits) < 25:   
            	continue

            #This check is because sometimes some of the fields are shifted so that something 
            # with underscores ends up in this field
            if '_' in Bits[15]:
                continue

            #Load up the buffer, reset it when we find a new ID
            if Bits[0] != currentID:
                if self.CheckBuffer():
                    self.WriteBuffer(OutHandle)
                currentID = Bits[0]
                self.Buffer = [Bits]
            else:
                self.Buffer.append(Bits)

        Handle.close()
        OutHandle.close()
