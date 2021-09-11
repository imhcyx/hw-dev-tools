#!/usr/bin/env python3

class PortGen():

    def __init__(self):
        self.__portlist = []
        self.INPUT = 0
        self.OUTPUT = 1

    def __str__(self):
        f = lambda x: \
            '    ' + \
            ['input   ', 'output  '][x[0]] + \
            ('[%2d:0]  ' % (x[1]-1) if x[1] > 0 else '        ') + \
            x[2]
        return ",\n".join(f(x) for x in self.__portlist)

    def _port_clear(self):
        self.__portlist = []

    def _port_s(self, direction, name):
        self.__portlist.append((direction, 0, name))

    def _port_v(self, direction, name, width):
        if width > 0:
            self.__portlist.append((direction, width, name))

class MasterSlavePortGen(PortGen):
    def __init__(self, is_master):
        PortGen.__init__(self)
        self._d1 = self.INPUT  if is_master else self.OUTPUT
        self._d2 = self.OUTPUT if is_master else self.INPUT

class AXI4LiteGen(MasterSlavePortGen):

    def __init__(self, is_master, prefix, addr_width, data_width):
        MasterSlavePortGen.__init__(self, is_master)
        self._pre = prefix
        self._addr_w = addr_width
        self._data_w = data_width

    def _axi4lite_if_ar(self):
        self._port_s(self._d2, self._pre + 'arvalid')
        self._port_s(self._d1, self._pre + 'arready')
        self._port_v(self._d2, self._pre + 'araddr', self._addr_w)
        self._port_v(self._d2, self._pre + 'arprot', 3)

    def _axi4lite_if_r(self):
        self._port_s(self._d1, self._pre + 'rvalid')
        self._port_s(self._d2, self._pre + 'rready')
        self._port_v(self._d1, self._pre + 'rresp', 2)
        self._port_v(self._d1, self._pre + 'rdata', self._data_w)

    def _axi4lite_if_aw(self):
        self._port_s(self._d2, self._pre + 'awvalid')
        self._port_s(self._d1, self._pre + 'awready')
        self._port_v(self._d2, self._pre + 'awaddr', self._addr_w)
        self._port_v(self._d2, self._pre + 'awprot', 3)

    def _axi4lite_if_w(self):
        self._port_s(self._d2, self._pre + 'wvalid')
        self._port_s(self._d1, self._pre + 'wready')
        self._port_v(self._d2, self._pre + 'wdata', self._data_w)
        self._port_v(self._d2, self._pre + 'wstrb', self._data_w // 8)

    def _axi4lite_if_b(self):
        self._port_s(self._d1, self._pre + 'bvalid')
        self._port_s(self._d2, self._pre + 'bready')
        self._port_v(self._d1, self._pre + 'bresp', 2)

    def gen(self):
        self._port_clear()
        self._axi4lite_if_ar()
        self._axi4lite_if_r()
        self._axi4lite_if_aw()
        self._axi4lite_if_w()
        self._axi4lite_if_b()

class AXI4LiteMasterIf(AXI4LiteGen):
    def __init__(self, prefix, addr_width, data_width):
        AXI4LiteGen.__init__(self,
                is_master=True,
                prefix=prefix,
                addr_width=addr_width,
                data_width=data_width)
        self.gen()

class AXI4LiteSlaveIf(AXI4LiteGen):
    def __init__(self, prefix, addr_width, data_width):
        AXI4LiteGen.__init__(self,
                is_master=False,
                prefix=prefix,
                addr_width=addr_width,
                data_width=data_width)
        self.gen()

class AXI4Gen(AXI4LiteGen):
    def __init__(self, is_master, prefix, addr_width, data_width):
        AXI4LiteGen.__init__(self, is_master, prefix, addr_width, data_width)

    def _axi4_if_ar(self):
        self._axi4lite_if_ar()
        self._port_v(self._d2, self._pre + 'arlen', 8)
        self._port_v(self._d2, self._pre + 'arsize', 3)
        self._port_v(self._d2, self._pre + 'arburst', 2)
        self._port_v(self._d2, self._pre + 'arlock', 1)
        self._port_v(self._d2, self._pre + 'arcache', 4)

    def _axi4_if_r(self):
        self._axi4lite_if_r()
        self._port_s(self._d1, self._pre + 'rlast')

    def _axi4_if_aw(self):
        self._axi4lite_if_aw()
        self._port_v(self._d2, self._pre + 'awlen', 8)
        self._port_v(self._d2, self._pre + 'awsize', 3)
        self._port_v(self._d2, self._pre + 'awburst', 2)
        self._port_v(self._d2, self._pre + 'awlock', 1)
        self._port_v(self._d2, self._pre + 'awcache', 4)

    def _axi4_if_w(self):
        self._axi4lite_if_w()
        self._port_s(self._d2, self._pre + 'wlast')

    def _axi4_if_b(self):
        self._axi4lite_if_b()

    def gen(self):
        self._port_clear()
        self._axi4_if_ar()
        self._axi4_if_r()
        self._axi4_if_aw()
        self._axi4_if_w()
        self._axi4_if_b()

class AXI4MasterIf(AXI4Gen):
    def __init__(self, prefix, addr_width, data_width):
        AXI4Gen.__init__(self,
                is_master=True,
                prefix=prefix,
                addr_width=addr_width,
                data_width=data_width)
        self.gen()

class AXI4SlaveIf(AXI4Gen):
    def __init__(self, prefix, addr_width, data_width):
        AXI4Gen.__init__(self,
                is_master=False,
                prefix=prefix,
                addr_width=addr_width,
                data_width=data_width)
        self.gen()
