#!/usr/bin/env python
import numpy as nmp
import graph
import constants

class RDS():

    def __init__(self):
        self.cnt = 0
        self.station_lock = False

    def process_line(self, line):
        self.pi, self.pt, self.gt, self.ps, self.rt = line

        if not self.station_lock:
            self.station_lock = True
            self.station = self.pi
            self.ps_persist = self.ps
            self.rt_persist = self.rt
        #if self.pi == self.station:
        self.cnt += 1
        self._augment_msg(self.ps, self.ps_persist)
        self._augment_msg(self.rt, self.rt_persist)

        self.ps_txt = ''.join(self.ps_persist)
        self.rt_txt = ''.join(self.rt_persist)
        self.msg = self.station, self.pt, self.gt, self.ps_txt, self.rt_txt, self.cnt

    def _augment_msg(self, segment, segment_persist):
        for n, x in enumerate(segment):
            if x == '\r':
                self._clear_msg(segment_persist)
            elif x != ' ' and ord(x) > 32 and ord(x) < 128:
                segment_persist[n] = x

    def _clear_msg(self, segment_persist):
        for n in range(len(segment_persist)):
            segment_persist[n] = ' '

def decode(bits, g, rds):
    """Decode Bit Stream"""
    bit0 = group_sync(bits)     # returns large number if not syncd

    for n in range(bit0, len(bits)-104, 104):
        frame = bits[n:n+104]
        line = (unpack_frame(frame))
        rds.process_line(line)

    if rds.station_lock:
        g.text(rds.msg)

def group_sync(bits):
    """Find Sync in Stream"""
    for n in range(len(bits)-104):
        frame = bits[n:n+104]
        if group_syndrome(frame) == constants.syndromes:
            return n
    return len(bits)                     # else if never sync'd

def group_syndrome(frame):
    """Calculate Group Syndrome"""
    syn = {}
    syn['A'] = block_syndrome(frame[:26])
    syn['B'] = block_syndrome(frame[26:52])
    syn['C'] = block_syndrome(frame[52:78])
    syn['D'] = block_syndrome(frame[78:])
    return syn

def block_syndrome(bits):
    """Calculate Block Syndrome"""
    syn = 0
    for n, bit in enumerate(bits):
        if bit:
            syn = nmp.bitwise_xor(syn, constants.parity[n])
    return syn

def unpack_frame(frame):
    """Unpack 104-bit Frame"""
    A = frame[:16]
    B = frame[26:42]
    C = frame[52:68]
    D = frame[78:94]
    pi = prog_id(A)
    pt = prog_type(B)
    gt = group_type(B)
    ps = prog_service(B, D, gt)
    rt = radiotext(B, C, D, gt)
    return [pi, pt, gt, ps, rt]

def prog_id(A):
    """Program Identification"""
    A = bit2int(A)
    K = 4096
    W = 21672
    if A >= W:
        pi0 = 'W'
        pi1 = W
    else:
        pi0 = 'K'
        pi1 = K
    pi2 = nmp.floor_divide(A - pi1, 676)
    pi3 = nmp.floor_divide(A - pi1 - pi2*676, 26)
    pi4 = A - pi1 - pi2*676 - pi3*26

    return pi0 + chr(pi2+65) + chr(pi3+65) + chr(pi4+65)

def prog_type(B):
    """Program Type"""
    pt_num = bit2int(B[6:11])
    try:
        return constants.pt_codes[pt_num]
    except:
        return 'ERR'

def group_type(B):
    """Group Type"""
    gt_num = bit2int(B[0:4])
    gt_ver = B[4]
    return str(gt_num) + chr(gt_ver + 65)      # 5th bit = Version (A|B)

def prog_service(B, D, gt):
    """Program Service"""
    ps = [' ']*8
    if gt == '0A':
        pschr = [0,0]
        cc = bit2int(B[-2:])
        pschr[0] = bit2int(D[0:8])
        pschr[1] = bit2int(D[8:16])
        ps[2*cc:2*cc+2] = [chr(pschr[i]) for i in range(2)]
    return ps

def radiotext(B, C, D, gt):
    """Radio Text"""
    rt = [' ']*64
    if gt == '2A':
        rtchr = [0,0,0,0]
        cc = bit2int(B[-4:])
        rtchr[0] = bit2int(C[0:8])
        rtchr[1] = bit2int(C[8:16])
        rtchr[2] = bit2int(D[0:8])
        rtchr[3] = bit2int(D[8:16])
        #rt[4*cc:4*cc+4] = [chr(rtchr[i]) if 32 < rtchr[i] < 128 else ' ' for i in range(4)]
        rt[4*cc:4*cc+4] = [chr(rtchr[i]) for i in range(4)]
    return rt

def bit2int(bits):
    """Convert bit string to integer"""
    word = 0
    for bit in bits:
        word = (word<<1) | bit
    return int(word)
