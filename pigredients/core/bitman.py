class BitSequence(object):
    def __init__(self, byte_data, word_length=8):
        self.value = byte_data
        self.bits_per_word = word_length
        
    def _bitLen(self):
        # Warning this does not take into account leading zeros, ie. 0000000010000000, you probbaly want to be using len(self)
        length = 0
        temp_val = self.value
        while (temp_val):
            temp_val >>= 1
            length += 1
        return(length)
        
    def __getitem__(self, val):
        return int(bin(self.value & (1 << val))[2:][0])
    
    def __setitem__(self, key, val):
        try:
            bool(val)
        except:
            raise TypeError("Possible bit values should evaluate to True of False, not %s" % val)
    
        if val:
            # set bit 'key' to 1
            self.value |= 1 << key
        else:
            # set bit 'key' to 0
            self.value &= ~(1 << key)
        
    def __len__(self):
        # work out how many words are needed to represent the value, and return this number of bits as its length
        return int(self._bitLen() + self.bits_per_word - (self._bitLen() % self.bits_per_word))
        
    def __str__(self):
        return "0b%s" % bin(self.value)[2:].zfill(len(self))

    def __int__(self):
        return self.value
        
    def __iter__(self):
        for bit in range(len(self)):
            yield self[bit]




if __name__ == '__main__':
    bitseq = BitSequence(0b0000000010101010)
    print bitseq
    bitseq = BitSequence(0b0000100010101010)
    print bitseq
    print "First : %d Second : %d" % (bitseq[0], bitseq[1])
    bitseq[0] = 1
    bitseq[1] = 1
    print "First : %d Second : %d Twentieth : %d" % (bitseq[0], bitseq[1],  bitseq[20])
    print bitseq
    bitseq[0] = True
    bitseq[1] = False
    bitseq[5] = None
    bitseq[6] = 1
    bitseq[7] = 1
    bitseq[20] = 1
    print "First : %d Second : %d" % (bitseq[0], bitseq[1])
    print bitseq
    
    bitseq1 = BitSequence(0b01)
    bitseq2 = BitSequence(0b10)
    
    print "Equal : %s" % bitseq1 == bitseq2
    print "Not Equal : %s" % bitseq1 != bitseq2
    print "%d Greater than %d : %s" % (bitseq1, bitseq2, bitseq1 > bitseq2)
    print "%d Less than %d : %s" % (bitseq1, bitseq2, bitseq1 < bitseq2)
    
    print "len(sequence) : %d" % len(bitseq)
    
    print "Printing bit sequece ..."
    for bit in bitseq:
        print bit
    
