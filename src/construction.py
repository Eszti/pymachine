import logging

from fst import FSA

class Construction(object):
    def __init__(self, name, control):
        self.name = name

        if not isinstance(control, FSA):
            raise TypeError("control has to be an FSA instance")
        self.control = control

    def check(self, seq):
        logging.debug("""Checking {0} construction for matching with
                      {1} machines""".format(self.name, seq))
        for machine in seq:
            self.control.read_symbol(machine.control)

    def run(self, seq):
        # read the sequence first, and give it to the control
        self.check(seq)

        # if control got into acceptor state, do something
        if self.control.in_final():
            return self.act(seq)
        else:
            return None

    def act(self, seq):
        logging.debug("""Construction matched, running action""")
        # arbitrary python code, now every construction will have it
        # hardcoded into the code, later it will be done by Machine objects
        pass

class AppendConstruction(Construction):
    def __init__(self, name, control, act_from_left=True, append_to_left=True):
        Construction.__init__(self)
        # when check is done, and an action is needed,
        # order of actions on machines is left to right or reverse
        self.act_from_left = act_from_left

        # when check is done, and an action is needed,
        # and we already have two machines chosen by the self.act_from_left
        # order traverse, on which machine do we want to append the other one
        self.append_to_left = append_to_left

class TheConstruction(Construction):
    """NOUN<DET> -> The NOUN"""
    def __init__(self):
        control = FSA()
        control.add_state("0", is_init=True, is_final=False)
        control.add_state("1", is_init=False, is_final=False)
        control.add_state("2", is_init=False, is_final=True)
        control.add_transition(self, "^the$", "0", "1")
        control.add_transition(self, "^NOUN.*", "1", "2")

        Construction.__init__(self, "TheConstruction", control)

    def act(self, seq):
        logging.debug("""TheConstruction matched, running action""")
        seq[1].control += "<DET>"
        return seq[1]

class DummyNPConstruction(Construction):
    """NP construction. NP -> Adj* NOUN"""
    def __init__(self):
        control = FSA()
        control.add_state("0", is_init=True, is_final=False)
        control.add_state("1", is_init=False, is_final=True)
        control.add_transition(self, "^ADJ.*", "0", "0")
        control.add_transition(self, "^NOUN.*", "0", "1")

        Construction.__init__(self, "DummyNPConstruction", control)

    def act(self, seq):
        logging.debug("""DummyNPConstruction matched, running action""")
        noun = seq[-1]
        adjs = seq[:-1]
        for adj in adjs:
            noun.append(adj)
        return noun


class ConstructionRunner(object):
    """ConstructionRunner takes a sentence (as a sequence of machines),
    a collection of constructions, and tries to match those constructions
    over a sequence of machines, which can be shorter than the whole sentence.
    Loop ends only when there is no construction that can be matched.
    """
    def __init__(self, constructions):
        self.constructions = constructions

    def run(self, seq):
        pass