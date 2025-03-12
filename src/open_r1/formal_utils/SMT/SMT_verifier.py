from z3 import *
set_param('parallel.enable', True)
# from Config import config
# from Utilities.TimeController import time_limit_calling
import threading
import time
from time import sleep

import z3


class Config:
    SMT_CHECK_TIME = 50

config = Config()

class MyThread(threading.Thread):
    def __init__(self, target, args=()):
        """
        https://www.cnblogs.com/hujq1029/p/7219163.html?utm_source=itdadao&utm_medium=referral
        """
        super(MyThread, self).__init__()
        self.func = target
        self.args = args

    def run(self):
        self.result = self.func(self.args)

    def get_result(self):
        try:
            return self.result
        except Exception:
            return z3.unknown

def time_limit_calling(func, args, timelimit):
    t1 = MyThread(target=func, args=args)
    t1.setDaemon(True)
    t1.start()
    t1.join(timelimit)
    return t1.get_result()


class Counterexample:
    kind = "?"
    assignment = {}


class SMT_verifier:
    tpl = []

    def initTpl(self, SMT2str ):
        vc_sections = [""]
        if 1==1 :
            for vc_line in SMT2str.splitlines():
                if "SPLIT_HERE_asdfghjklzxcvbnmqwertyuiop" in vc_line:
                    vc_sections.append("")
                else:
                    vc_sections[-1] += vc_line
        assert len(vc_sections) == 5

        self.tpl = [vc_sections[0]]

        for i in range(2, 5):
            self.tpl.append(vc_sections[1] +"\n"+ vc_sections[i]+"\n")

    def verify(self, Can_I, SMT2str):
        sol = z3.Solver()
        sol.set(auto_config=False)
        sol.set("timeout", config.SMT_CHECK_TIME)
        
        # assert "(set-logic LIA)" in SMT2str

        if len(self.tpl) <= 0:
            self.initTpl(SMT2str)

        Can_I_smt = Can_I[7:-1]
        for i in range(3):
            s = self.tpl[0]+"\n" + Can_I_smt +"\n"+ self.tpl[i + 1]+"\n"  # wait to see
            # s = self.tpl[0]  + self.tpl[i + 1]  # wait to see
            # print ("--->", Can_I, "======>"*4  )
            # print ( s )
            sol.reset()
            # try:
            decl = z3.parse_smt2_string(s)
            # except Exception as ex :
                # print(f"SMTLIB2 False! {str(ex)}: --> Can_I_smt : {Can_I_smt} --> Can_I: {Can_I} \n -> {s}")
                # raise 
                # return None, False
            sol.add(decl)
            r = time_limit_calling(sol.check, (), config.SMT_CHECK_TIME)

            kind = "?"
            ce = {}
            if z3.sat == r:  # we got a counterexample
                m = sol.model()
                if i == 0 or i == 2:
                    for x in m:
                        v = str(x)
                        if v in ['inv-f', 'post-f', 'pre-f', 'trans-f', 'div0', 'mod0']:
                            continue
                        if "_" in v:
                            continue
                        ce[v] = m[x]
                    kind = "p" if i == 0 else "n"
                else:
                    m1, m2 = {}, {}
                    for x in m:
                        v = str(x)
                        if v in ['inv-f', 'post-f', 'pre-f', 'trans-f', 'div0', 'mod0']:
                            continue
                        if "_" in v:
                            continue
                        const = m[x]
                        if v.endswith("!"):
                            m2[v[:-1]] = const
                        else:
                            m1[v] = const
                    ce = (m1, m2)
                    kind = "i"
                counterexample = Counterexample()
                counterexample.kind = kind
                counterexample.assignment = ce
                return counterexample,True

            elif z3.unknown == r: # timeout
                print(i)
                raise TimeoutError("SMT Checking is OOT:    " + str(Can_I))

            else:
                assert z3.unsat == r #we pass this one, continue
                continue

        return None,True  # we find the answer



