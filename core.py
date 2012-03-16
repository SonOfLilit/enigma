"""
gets many variables from the ocnfiguratoin file:
    rotors
    initial rotors shit
    pluboard
    ALPHABET
    alpha_len
"""

from trace import trace

# AUR: see PEP8. It really helps to follow your language's style conventions
class enigma(object):
    """ machine state. shift of the rotors.
    attributes:
        rotors = a dict num:rotor. rotor is a list that maps numbers 0...n > 0....n
        shift = a list, the position of each rotor.
        rotors number
        alpha_len
        plugboard = is not implemented yet.
        ALPHBET"""

    # AUR: can you explain why this is here?
    attributes = ['rotors', 'shift', 'plugboard']
    #extra_attributes = [rotors_num, alpha_len, alphabet]
    
    # AUR: There seem to be quite a few different ways to initialize
    # the class. Is there a reason to support more than one?
    def __init__(self, rotors = {}, shift = [], rotors_num = 0, alpha_len = 0, plugboard = [], alphabet = []):
        self.rotors = rotors
        self.shift = shift
        self.rotors_num = rotors_num
        # AUR: Does it make any sense to have alpha_len != len(alphabet) ?
        self.alpha_len = alpha_len
        self.plugboard = plugboard
        self.alphabet = alphabet
    # AUR: It really confused me that there were no empty lines between functions
    def calculate_extra_attributes(self):
        ''' use rotors to calc rotors_num, alphabet, alpha_leb '''
        # AUR: Wait, what? Either the logic is wrong or the naming is wrong (guess second)
        self.rotors_num = (len(self.rotors) + 1 ) / 2
        self.alpha_len = len(self.rotors[0]) # check rotors length
        self.alphabet = range(self.alpha_len)
    def configure(self):   # could be more orthogonal : conf_file = conf.py
        ''' the enigma gets it's attributes from the conf file '''
        # AUR: importing in non-global scope is frowned upon, and I
        # agree it usually just confuses things
        import conf
        # maybe more efficiant: for att in enigma.attributes:
            # self.att = conf.att()
        self.rotors = conf.rotors()
        self.shift = conf.shift()
        trace(self.shift)
        self.plugboard = conf.plugboard()


        self.calculate_extra_attributes()
    def rotate_one_rotor(self, rotor_num):
        """rotate one rotor forward """
        # AUR: the use of "return" seems redundant to me. could be e.g. "if not something: do something"
        if rotor_num == 0:
            # AUR: maybe the reason for this could've been explained better by better naming or a comment?
            return
        else:
            # AUR: maybe self.shift[rotor_num] = (self.shift[rotor_num] + 1) % self.alpha_len ?
            self.shift[rotor_num] += 1
            self.shift[rotor_num] = self.shift[rotor_num] % self.alpha_len
            return

    def rotate(self):
        """ rotate each rotor, if needed"""
        self.rotate_one_rotor(self.rotors_num - 1)
        # AUR: This feels like a natural place for a while loop, I think...
        # The main problem with using for is that there are now all these numbers the reader
        # needs to figure out and keep track of that are not explained naturally by the code
        # (rotors_num -2; 0; -2) 
        for i in range(self.rotors_num - 2, 0, -1):
            if self.shift[i + 1] == 0:
                self.rotate_one_rotor(i)
            else:
                break

        return self


    # AUR: Maybe you should name this function according to its function in the enigma?
    # I can't figure out why this substituting is done...
    def sub_by_rotor(self, rotor_num, num):
        """ substitute the number by one rotor"""
        trace(num, '>')
        assert num in self.alphabet
        # AUR: You're doing all these rotations all the time, and your code is full of
        # increment-then-%... Maybe the codebase would be clearer if you used a
        # "modular number" class?
        #
        # Something like:
        # >>> a = ModNum(16, 5)
        # >>> a
        # 5mod16
        # >>> a + 1
        # 6mod16
        # >>> a = a + a + a + a
        # >>> a
        # 4mod16
        #
        # or maybe the less magical:
        # >>> a = Rotor(6, 5)
        # >>> a
        # <Rotor 6>
        # >>> a.value
        # 5
        # >>> a.increase()
        # >>> a.value
        # 0
        # >>> a.decrease()
        # >>> a.value
        # 5
        #
        # In general, a very good thought technique when programming is asking "what are my
        # core concepts?" and making those easy to "speak in" without needing to do
        # bookkeeping.

        num += self.shift[rotor_num]
        num = num % self.alpha_len
        num = self.rotors[rotor_num][num]
        num -= self.shift[rotor_num]
        num = num % self.alpha_len
        trace(num, '>')
        return num

    def sub_by_all_rotors(self, num):
        """ substitute the number by all the rotors """
        # AUR: Any special reason to use range and not xrange? You should always prefer the latter
        for i in range(self.rotors_num - 1, -(self.rotors_num - 1), -1):
            num = self.sub_by_rotor(i, num)
        return num


    def sub_plugboard(self, num):
        """ substitute the number using the pkugboard """
        # AUR: wait, what? :P
        pass

    def click(self, p_num):
        """ this is the main enigma function: encript a letter and rotate the rotors """
        e_num = self.sub_by_all_rotors(p_num)
        self.rotate()
        return e_num

# AUR: It would be really cool to model an enigma "physically", like
# Amos proposed in the morals.txt file.
#
# (I tried to write some pseudo code for what I meant and ended up
# with quite a complete implementation, so you can read it below to
# figure what I mean.)
#
# That sounds like the most elegant way to write this, but I'm not
# sure I would have taken it immediately. The enigma sounds simple
# enough that I'd probably rather have one function that is a bit
# hairy doing the core of encryption/decryption and avoid all the code
# needed to establish the concepts of the physical simulation (like
# Connections).
#
# The simulation solution is something like this (after I wrote this I
# read some wikipedia and it turns out I didn't remember the
# reflection right and forgot the plugboard):
#
class Connection(object):
    def __init__(self, this, next):
        self.this = this
        self.next = next

    def transform_character(self, char):
        return self.next.transform_character(self.this.transform_character(char))


class Enigma(object):
    def __init__(self, wheel_configurations):
        self.wheels = []
        
        # build wheels and order them wheel0 -> wheel1 -> ...
        next_wheel = None
        for conf in wheel_configurations:
            wheel = Wheel(conf, next_wheel))
            self.wheels.append(wheel)
            next_wheel = wheel

        # build connections: wheel0 -> wheel1 -> ... -> wheel_n -> reverse_wheel_n-1 -> ... reverse_wheel0
        # hope I remember the enigma configuration correctly :-)
        connections = self.wheels[0]
        for wheel in self.wheels[1:]:
            connections = Connection(connections, wheel)
        reverse_wheels = self.wheels[:-1]
        reverse_wheels.reverse()
        for wheel in reverse_wheels:
            connections = Connection(connections, Reverse(wheel))
        
        self.connections = connections

    def setup(self, positions):
        for wheel, position in zip(self.wheels, positions):
            wheel.setup(position)

    def transform_character(self, char):
        char = self.connections.transform_character(char)
        self.rotate(self.wheels[0])
        return char


class Wheel(object):
    def __init__(self, pairs):
        ...

    ...

    def transform_character(self, char):
        return self.table[(self.position + char) % len(self)]

    def reverse_transoform_character(self, char):
        return self.reverse_table[(self.position + char) % len(self)]

    def rotate(self):
        self.position = (self.position + 1) % len(self)
        if self.position == 0 and self.next:
            self.next.rotate()


class Reverse(object):
    """
    Wraps a wheel, uses it in reverse order. Fully affected by the
    wheel being rotated, reset etc'.
    """
    def __init__(self, wheel):
        self.wheel = wheel

    def transform_character(self, char): return self.wheel.reverse_transoform_character(char)

    def reverse_transoform_character(self, char): return self.wheel.transform_character(char)
