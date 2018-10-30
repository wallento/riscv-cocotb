from collections import deque

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import Timer, RisingEdge, FallingEdge

from riscvmodel.model import Model
from riscvmodel.program.tests import ADDITest

class Testbench(object):
    def __init__(self, variant, dut):
        self.dut = dut
        self.sig_clk = self.dut.__getattr__(self._clk)
        self.sig_reset = self.dut.__getattr__(self._reset)
        cocotb.fork(Clock(self.sig_clk, 2).start())

        self.model = Model(variant)

    @cocotb.coroutine
    def reset(self, duration = 10):
        if self._reset_polarity:
            self.sig_reset <= 1
        else:
            self.sig_reset <= 0
        yield Timer(duration)
        yield RisingEdge(self.sig_clk)
        if self._reset_polarity:
            self.sig_reset <= 0
        else:
            self.sig_reset <= 1
        cocotb.fork(self.busif())

    @cocotb.coroutine
    def basic(self):
        self.insns = deque(ADDITest().insns)
        for i in range(10):
            yield RisingEdge(self.sig_clk)

    def fetch(self, pc: int):
        insn = self.insns.popleft()
        self.model.execute(insn)
        return insn.encode()

    def lb(self, addr: int):
        pass

    def lh(self, addr: int):
        pass

    def lw(self, addr: int):
        pass

    def sb(self, addr: int, data: int):
        pass

    def sh(self, addr: int, data: int):
        pass

    def sw(self, addr: int, data: int):
        pass