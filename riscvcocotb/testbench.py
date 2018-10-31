from collections import deque

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import Timer, RisingEdge, FallingEdge
from cocotb.result import TestFailure, TestSuccess

from riscvmodel.golden import GoldenUnbuffered, GoldenProgramEndException, traces_from_rvfi
from riscvmodel.program.tests import ADDITest
from riscvmodel.types import RVFISignals
from riscvmodel.code import decode


class Testbench(object):
    def __init__(self, variant, dut, rvfi):
        self.dut = dut
        self.sig_clk = self.dut.__getattr__(self._clk)
        self.sig_reset = self.dut.__getattr__(self._reset)
        self.rvfi = rvfi
        cocotb.fork(Clock(self.sig_clk, 2).start())
        self.model = GoldenUnbuffered(variant)

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
        cocotb.fork(self.rvfi_monitor())

    @cocotb.coroutine
    def basic(self):
        self.model.load_program(ADDITest())
        self.model.reset()
        for i in range(20):
            yield RisingEdge(self.sig_clk)

    @cocotb.coroutine
    def rvfi_monitor(self):
        while True:
            if self.rvfi.valid.value == 1:
                try:
                    rvfi = self.rvfi_extract_values(self.rvfi)
                    self.model.commit(traces_from_rvfi(rvfi), insn = decode(rvfi.insn))
                except ValueError:
                    raise TestFailure(str(ValueError()))
                except GoldenProgramEndException:
                    raise TestSuccess()
                self.dut._log.info("Comitted")
            yield RisingEdge(self.sig_clk)

    @staticmethod
    def rvfi_lookup(dut) -> RVFISignals:
        signals = {}
        for v in RVFISignals._fields:
            signals[v] = dut.__getattr__("rvfi_{}".format(v))
        return RVFISignals()._replace(**signals)

    def rvfi_extract_values(self, signals: RVFISignals) -> RVFISignals:
        values = {}
        for v in RVFISignals._fields:
            values[v] = signals.__getattribute__(v).__int__()
        return RVFISignals()._replace(**values)


    def fetch(self, pc: int):
        insn = self.model.fetch(pc)
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