import cocotb
from cocotb.triggers import Timer, RisingEdge, FallingEdge
from riscvcocotb.testbench import Testbench

from riscvmodel.variant import RV32I

class PicoRV32Testbench(Testbench):
    _clk = "clk"
    _reset = "resetn"
    _reset_polarity = False

    def __init__(self, dut):
        super().__init__(RV32I, dut)
        dut.mem_ready <= 0
        dut.irq <= 0

    @cocotb.coroutine
    def busif(self):
        while True:
            if int(self.dut.mem_valid) == 1:
                if int(self.dut.mem_instr) == 1:
                    insn = self.fetch(int(self.dut.mem_addr))
                    self.dut.mem_rdata <= insn
                    self.dut.mem_ready <= 1
                    yield FallingEdge(self.sig_clk)
                    self.dut.mem_ready <= 0
            else:
                yield FallingEdge(self.sig_clk)



@cocotb.test(stage=0)
def test_basic(dut):
    tb = PicoRV32Testbench(dut)

    yield tb.reset()
    yield tb.basic()
