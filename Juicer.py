#Reduces rows in bcp files downloaded from which has been parsed, limiting it to useful data

import os
import sys
import getopt
import string


class Juicer:

    def __init__(self, InPath, OutPath):
        self.InputFilePath = InPath
        self.OutFilePath = OutPath

    def Main(self):
        #We're going to cut out any subsnps in the file in which no populations have
        # a minor allele frequency (MAF) >= 1%
        self.ParseFile(self.InputFilePath, self.OutFilePath)

    def ParseFile(self, InPath, OutPath):
        Handle = open(InPath, 'r')
        OutHandle = open(OutPath, 'w')
        Header = Handle.readline()
        Header = "SubSNP_ID\tAllele_ID\tEAS\tEUR\tAFR\tAMR\tSAS\n"
        OutHandle.write(Header)
        
        counter = 0
        currentID = ""
        self.Buffer = []
        for line in Handle:
            counter +=1
            if counter % 1000000 ==0 :
                print ("Progress: Read %s lines"%counter)

            Bits = line.strip().split()
            #[0] is subsnp_id, an id assigned to each submitted SNP by dbSNP
            #[1] is pop_id, which matches up with a population in the Population table
            #[2] is allele_id, which matches up with an allele in the Allele table
            #[3] is freq, the allele frequency 
            if Bits[0] != currentID:
                if self.CheckBuffer():
                    self.WriteBuffer(OutHandle)
                currentID = Bits[0]
                self.Buffer = [Bits]
            else:
                self.Buffer.append(Bits)
            
        Handle.close()
        OutHandle.close()

    def CheckBuffer(self):
        #Makes sure the buffer is appropriate to write, making sure
        # at least one population has a MAF of greater than 1%
        for Bits in self.Buffer:
            if len(Bits) < 4:
                return False
            freq = float(Bits[3])
            #Because the file contains both major and minor alleles, we need to
            # check both bounds to make sure there are no false positives from
            # major allele frequencies
            if freq < 0.5 and freq > 0.01:
                return True

        #If the condition is not met for any population in the buffer (or if the 
        # buffer is empty, as it should be the first time this method is called,
        # we won't write it
        return False

    def WriteBuffer(self, OutHandle):
        #Takes the bits of lines from the buffer and writes them to the output
        # file, two lines at a time.
        allele1 = self.Buffer[0]
        allele2 = self.Buffer[1]

        line1 = allele1[0] + "\t" + allele1[2]
        line2 = allele2[0] + "\t" + allele2[2]
        oneoff = True

        for Bits in self.Buffer:
            if oneoff:
                line1 += "\t" + Bits[3]
            else:
                line2 += "\t" + Bits[3]
            oneoff = not oneoff

        line1 += "\n"
        line2 += "\n"

        OutHandle.write(line1)
        OutHandle.write(line2)