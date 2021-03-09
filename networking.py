# This Python file uses the following encoding: utf-8


class message:
    def __init__(self, payload=None, flag_send=False, flag_read=False, flag_SYN=False, flag_ACK=False):
        flags = 0  # 0bxxxxxxxx: 0b00000[ACK][SYN][send 0 / read 1]

        if flag_send == flag_read:
            raise ValueError('Message construction error (flags)')

        if flag_read is True:
            flags = bin(flags | 0b00000001)
        if flag_SYN is True:
            flags = bin(flags | 0b00000010)
        if flag_ACK is True:
            flags = bin(flags | 0b00000100)

        # Message is flags only. Already constructed above
        if (not payload and flag_send and     flag_SYN and     flag_ACK)
        or (not payload and flag_send and not flag_SYN and     flag_ACK)
        or (not payload and flag_read and     flag_SYN and     flag_ACK)
        or (not payload and flag_read and not flag_SYN and     flag_ACK):
            print('1')
        # TODO: construct msg
        return

        # Add payload to flags
        if     payload and flag_send and     flag_SYN and not flag_ACK:
            print('type 2')
        # TODO: construct msg
        return


class networking:
    def __init__(self):
        pass
