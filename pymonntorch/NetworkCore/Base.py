import torch

from pymonntorch.NetworkCore.TaggableObject import *


class NetworkObjectBase(TaggableObjectBase):
    def __init__(self, tag, network, behavior):
        super().__init__(tag)

        self.network = network
        self.behavior = behavior
        if type(behavior) == list:
            self.behavior = dict(zip(range(len(behavior)), behavior))
        self.behavior = torch.nn.ModuleDict(self.behavior)

        for k in sorted(list(self.behaviour.keys())):
            if self.behaviour[k].set_variables_on_init:
                network._set_variables_check(self, k)

        self.analysis_modules = torch.nn.ModuleList()

    def register_behavior(self, key, behavior, initialize=True):
        """
        :param key: key to be used to access behavior
        :param behavior: behavior to be registered
        :param initialize: if true, behavior will be initialized
        :return: the behavior

        register behavior to network object
        """
        self.behavior[key] = behavior
        self.network._add_key_to_sorted_behavior_timesteps(key)
        self.network.clear_tag_cache()

        if initialize:
            behavior.set_variables(self)
            behavior.check_unused_attrs()

        return behavior

    def register_behaviors(self, behavior_dict):
        """
        :param behavior_dict: dictionary of behaviors to be registered
        :return: the behavior_dict
        
        register multiple behaviors to network object
        """
        for key, behavior in behavior_dict.items():
            self.register_behavior(key, behavior)
        return behavior_dict

    def remove_behavior(self, key_tag_behavior_or_type):
        """
        :param key_tag_behavior_or_type: key, tag, behavior or type of behavior to be removed
        :return:
        
        remove behavior from network object
        """
        remove_keys = []
        for key in self.behavior:
            b = self.behavior[key]
            if (
                key_tag_behavior_or_type == key or 
                key_tag_behavior_or_type in b.tags or 
                key_tag_behavior_or_type == b or 
                key_tag_behavior_or_type == type(b)
            ):
                remove_keys.append(key)

        for key in remove_keys:
            self.behavior.pop(key)

    def set_behaviors(self, tag, enabeled):
        """
        :param tag: tag of behaviors to be set
        :param enabeled: if true, behaviors will be enabeled
        :return:
        
        set enabeled state of behaviors
        """
        if enabeled:
            print('activating', tag)
        else:
            print('deactivating', tag)
        for b in self[tag]:
            b.behavior_enabled = enabeled

    def deactivate_behaviors(self, tag):
        """
        :param tag: tag of behaviors to be deactivated
        :return:
        
        deactivate behaviors
        """
        self.set_behaviors(tag, False)

    def activate_behaviors(self, tag):
        """
        :param tag: tag of behaviors to be activated
        :return:
        
        activate behaviors
        """
        self.set_behaviors(tag, True)


    def find_objects(self, key):
        result = []

        if key in self.behavior:
            result.append(self.behavior[key])

        for bk in self.behavior:
            behavior = self.behavior[bk]
            result += behavior[key]

        for am in self.analysis_modules:
            result += am[key]

        return result

    def register_analysis_module(self, module):
        module._attach_and_initialize_(self)

    def get_all_analysis_module_results(self, tag, return_modules=False):  # TODO: check it after AnalysisModule is implemented
        result = {}
        modules = torch.nn.ModuleDict()
        for module in self[tag]:
            module_results = module.get_results()
            for k in module_results:
                result[k] = module_results[k]
                modules[k] = module

        if return_modules:
            return result, modules
        else:
            return result

    def buffer_roll(self, mat, new=None):
        mat[1:len(mat)] = mat[0:len(mat) - 1]

        if new is not None:
            mat[0]=new

        return mat

    def get_torch_tensor(self, dim):
        return torch.zeros(dim).to(def_dtype)

    def _get_mat(self, mode, dim, scale=None, density=None, plot=False, kwargs={}): # mode in ['zeros', 'zeros()', 'ones', 'ones()', 'uniform(...)', 'lognormal(...)', 'normal(...)']
        prefix = 'torch.'
        if mode == 'random' or mode == 'rand' or mode == 'rnd' or mode == 'uniform':
            mode = 'rand'

        if type(mode) == int or type(mode) == float:
            mode = 'ones()*'+str(mode)

        mode = prefix + mode
        if '(' not in mode and ')' not in mode:
            mode += '()'

        if mode not in self._mat_eval_dict:
            a1 = 'size=dim'
            if '()' in mode:#no arguments => no comma
                ev_str = mode.replace(')', a1+',**kwargs)')
            else:
                ev_str = mode.replace(')', ','+a1+',**kwargs)')

            self._mat_eval_dict[mode] = compile(ev_str, '<string>', 'eval')

        result = eval(self._mat_eval_dict[mode])

        if density is not None:
            if type(density) == int or type(density) == float:
                result = (result * (torch.rand(dim) <= density))
            elif type(density) is torch.tensor:
                result = (result * (torch.rand(dim) <= density[:, None]))

        if scale is not None:
            result *= scale

        if plot:
            import matplotlib.pyplot as plt
            plt.hist(result.flatten(), bins=30)
            plt.show()

        return result.to(def_dtype)


    def get_random_tensor(self, dim, density=None, clone_along_first_axis=False, rnd_code=None):#rnd_code=torch.rand(dim)
        if rnd_code is None:
            result = torch.rand(dim)
        else:
            if 'dim' not in rnd_code:
                if rnd_code[-1] == ')':
                    rnd_code = rnd_code[:-1]+',size=dim)'
                else:
                    rnd_code = rnd_code+'(size=dim)'
            result = eval(rnd_code)

        if density is None:
            result = result.to(def_dtype)
        elif type(density) == int or type(density) == float:
            result = (result * (torch.rand(dim) <= density)).to(def_dtype)
        elif type(density) is torch.tensor:
            result = (result * (torch.rand(dim) <= density[:, None])).to(def_dtype)


        if not clone_along_first_axis:
            return result
        else:
            return torch.cat([result[0] for _ in range(dim[0])])


    def get_buffer_mat(self, dim, size):
        return torch.cat([self.get_torch_tensor(dim) for _ in range(size)]).reshape(size, *dim)

    def set_iteration(self, iteration):
        self.iteration = iteration