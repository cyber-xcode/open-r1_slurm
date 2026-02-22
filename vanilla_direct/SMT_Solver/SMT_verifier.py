
from z3 import *
set_param('parallel.enable', True)
# from Config import config
config_SMT_CHECK_TIME = 60 
# from Utilities.TimeController import time_limit_calling


import threading
import time
from time import sleep

import z3


class MyThread(threading.Thread):
    def __init__(self, target, args=()):
        super(MyThread, self).__init__()
        self.func = target
        self.args = args

    def run(self):
        # 接受返回值
        self.result = self.func(self.args)

    def get_result(self):
        # 线程不结束,返回值为None
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

    def initTpl(self, path2SMT=None,SMT2str=None):
        assert any([ path2SMT is not None , SMT2str is not None ])
        vc_sections = [""]
        if path2SMT:
            with open(path2SMT, 'r') as vc:
                for vc_line in vc.readlines():
                    if "SPLIT_HERE_asdfghjklzxcvbnmqwertyuiop" in vc_line:
                        vc_sections.append("")
                    else:
                        vc_sections[-1] += vc_line
        else :
            for vc_line in SMT2str.splitlines():
                if "SPLIT_HERE_asdfghjklzxcvbnmqwertyuiop" in vc_line:
                    vc_sections.append("")
                else:
                    vc_sections[-1] += vc_line+"\n"
            
        assert len(vc_sections) == 5

        self.tpl = [vc_sections[0]]

        for i in range(2, 5):
            self.tpl.append(vc_sections[1] + vc_sections[i])

    def verify(self, Can_I, path2SMT=None,SMT2str = None ):
        sol = z3.Solver()
        sol.set(auto_config=False)
        sol.set("timeout", config_SMT_CHECK_TIME)

        if len(self.tpl) <= 0:
            self.initTpl(path2SMT=path2SMT,SMT2str=SMT2str)

        Can_I_smt = Can_I[7:-1]
        for i in range(3):
            s = self.tpl[0] + Can_I_smt + self.tpl[i + 1]  # wait to see
            sol.reset()
            try:
                decl = z3.parse_smt2_string(s)
            except:
                # print("SMTLIB2 False!")
                return None, False
            sol.add(decl)
            r = time_limit_calling(sol.check, (), config_SMT_CHECK_TIME)

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




