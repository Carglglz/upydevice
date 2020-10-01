from upydevice import get_serial_port_data


def test_serial():
    d, m = get_serial_port_data('/dev/cu.SLAB_USBtoUART')
    print(d, m)
    assert d
    assert m
