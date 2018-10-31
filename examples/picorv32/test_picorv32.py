import cocotb

from riscvcocotb.cores.picorv32 import PicoRV32Testbench

@cocotb.test(stage=0)
def test_basic(dut):
    tb = PicoRV32Testbench(dut)

    yield tb.reset()
    yield tb.basic()
