import sys
import inspect
from pathlib import Path

file_ = Path(__file__)
modulespath = '{}/modules'.format(file_.resolve().parents[1])
sys.path.insert(1, modulespath)

from nemo.backends.pytorch.nm import NeuralModule
from nemo_gquant_modules.nemoBaseNode import FeedProperty

TEMPLATE = """from gquant.dataframe_flow import Node
from .nemoBaseNode import NeMoBase
import nemo
import {}
"""

CLASS_TEMP = """


class {}(NeMoBase, Node):
    def init(self):
        NeMoBase.init(self, {})
"""


def gen_module_file(module, overwrite=None):
    file_str = TEMPLATE.format(module.__name__)

    nodecls_list = []

    for item in inspect.getmembers(module):
        if inspect.ismodule(item[1]):
            if item[1].__package__.startswith('nemo'):
                for node in inspect.getmembers(item[1]):
                    if inspect.isclass(node[1]):
                        nodecls = node[1]
                        if nodecls in nodecls_list:
                            continue

                        if issubclass(nodecls, NeuralModule):
                            if nodecls.__module__ == 'nemo.backends.pytorch.nm':
                                continue
                            try:
                                # p_inports = node[1].input_ports
                                # p_outports = node[1].output_ports
                                # feeder = FeedProperty({})
                                # inports = p_inports.fget(feeder)
                                # outports = p_outports.fget(feeder)

                                init_fun = node[1].__init__
                                sig = inspect.signature(init_fun)
                                skip = False
                                for key in sig.parameters.keys():
                                    if key == 'self':
                                        # ignore the self
                                        continue
                                    para = sig.parameters[key]
                                    if para.default != inspect._empty:
                                        if para.default.__class__.__name__ == 'type' or para.default.__class__.__name__ == 'DataCombination':
                                            print(para.default, para)
                                            skip = True
                                            break
                                if skip:
                                    print(node[0], 'find class arg', para.default.__class__.__name__)
                                    continue

                                class_name = node[1].__module__ + '.' + node[1].__name__
                                file_str += CLASS_TEMP.format(node[0] + "Node",
                                                              class_name)
                                nodecls_list.append(nodecls)
                            except Exception as e:
                                print(e)
                                print(node[0], 'is not compatible, as it uses instance for input/output ports')
                                continue

    if overwrite is not None:
        module_name = overwrite
    else:
        module_name = module.__name__.split('.')[-1]
    with open('../modules/nemo_gquant_modules/' + module_name + '.py', 'w') as f:
        f.write(file_str)


import nemo.backends.pytorch.tutorials
gen_module_file(nemo.backends.pytorch.tutorials)

import nemo.backends.pytorch.common
gen_module_file(nemo.backends.pytorch.common)

import nemo.collections.asr
gen_module_file(nemo.collections.asr)

import nemo.collections.cv
gen_module_file(nemo.collections.cv)

import nemo.collections.nlp.nm
gen_module_file(nemo.collections.nlp.nm, 'nlp')

import nemo.collections.simple_gan
gen_module_file(nemo.collections.simple_gan)

import nemo.collections.tts
gen_module_file(nemo.collections.tts)

