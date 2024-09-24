from typing import Union, Tuple, List, Any, Dict


from python_lib.utils import _iterate_over_structure
from python_lib.log import log_branch_report, log_report, print_log, \
    _NOTE, _WARNING, _ERROR, _CRITICAL


## ========================================================================== ##
##                            DataStructureChecker                            ##
## ========================================================================== ##
class DataStructureChecker:
    def __init__(self, data:dict, reference:dict):
        self.data = data
        self.reference = reference

        self.log = []
        self.done = False
        self.valid = None


    def is_valid(self) -> bool:
        if not self.done:
            self._run_check()
        return self.valid


    def print_log(self, min_importance) -> None:
        if not self.done:
            self._run_check()
        print_log(log=self.log, min_importance=min_importance)


    def _run_check(self) -> bool:
        self.log = []
        if isinstance(self.data, type(None)):
            self.log_report(importance=_CRITICAL, message="File is empty.")
            self.valid = False
        else:
            error_detected = self.check_data_consistency(
                data=self.data,
                reference=self.reference,
            )
            self.valid = not error_detected

        self.done = True
        return 
    

    # wrapper functions for logging
    def log_branch_report(self, importance:int, branch:list, message:str, 
        ) -> None:
        self.log = log_branch_report(log=self.log, importance=importance, 
            branch=branch, message=message, message_limit=240,
            )


    def log_report(self, importance:int, message:str) -> None:
        self.log = log_report(log=self.log, importance=importance, 
                message=message, message_limit=240,
            )


    ## ========================== flatten_hierarchy ========================= ##
    def flatten_hierarchy(
            self,
            structure: Union[dict, list],
        ) -> List[Tuple[List[Union[str, int]], Any]]:
        """ Given a nested structure returns a list of tuples. 
        The first element of tuple is `branch` (list of structure members) 
        that leads to `leaf` (the value stored at the end of the branch).

        :param structure: Nested structure represented by `dict` and `list`. 
            Notice, `list` where items are not `dict` or `list` 
            is reported as leaf (the iteration stops), includes empty list.
        :return: List of Tuples, each tuple includes `branch` and `leaf`.
        """
        hierarchy = []
        for (member_list, value) in \
            _iterate_over_structure(structure=structure):
            hierarchy.append((member_list, value))
        return hierarchy


    ## ============================ verify_branch =========================== ##
    def verify_branch(
            self,
            branch:List[Union[str, int]], 
            reference:Union[list,dict],
        ) -> Tuple[bool, list, Union[str, int]]:
        """ Check whether the branch follows the reference structure.

        :param branch: List of internodes.
        :param reference: Nested structure represented by `dict` and `list`. 
            Notice, every list has only `index==0`.
        :return: Tuple:
            - valid_branch: If True, `branch` exists according to `reference`. 
                If False, `branch` has non-existent `internode`.
            - valid_internodes: List of internodes that are valid 
                (if valid_branch, then `branch` == `valid_internodes`).
            - invalid_internode: If `valid_branch == False` then `internode` 
                points to the first invalid `internode` in the `branch` according 
                the `reference`, else `None`.
        """
        valid_indetnodes = []
        node = reference

        if len(branch) == 0:
            return False, valid_indetnodes, None

        for internode in branch:

            # catch in-branch error
            if isinstance(internode, int):
                try:
                    node = node[0]
                    valid_indetnodes.append(internode)
                except TypeError as e:
                    return False, valid_indetnodes, internode
            else:
                try:
                    node = node[internode]
                    valid_indetnodes.append(internode)
                except Exception as e:
                    return False, valid_indetnodes, internode
                
        # value to return when no error
        return True, valid_indetnodes, None


    ## ======================= check_data_consistency ======================= ##
    def check_data_consistency(
            self,
            data:dict, 
            reference:dict,
        ) -> List[Dict[str, Union[str,int]]]:
        """ Top-level function that checks the provided data structure agains a 
        reference structure. Retunrs a log informing 

        :param data: Nested structure represented by `dict` and `list`. 
        :param reference: Nested structure represented by `dict` and `list`. 
        :return: List of `dict`, every `dict` includes keys:
            - importance: Importance of logged message.
            - message: Message intended for the user to see.
        """
        flat_hierarchy = self.flatten_hierarchy(structure=data)
        no_warnings_or_errors = True
        error_detected = False

        for branch, value in flat_hierarchy:
            if value is None:
                self.log_branch_report(
                    importance=_WARNING, 
                    branch=branch, 
                    message="branch has no content.",
                )
                no_warnings_or_errors = False
            else:
                exists, valid_internodes, invalid_internode = \
                    self.verify_branch(
                        branch=branch, 
                        reference=reference,
                    )
                if not exists:
                    self.log_branch_report(
                        importance=_ERROR, 
                        branch=valid_internodes+[invalid_internode], 
                        message=\
                            f"branch includes invalid '{invalid_internode}'"\
                            f" (entries not conforming to the reference "\
                            f"structure are skipped), contains '{value}'"\
                    )
                    error_detected = True
                    no_warnings_or_errors = False
        
        if no_warnings_or_errors:
                self.log_report(importance=_NOTE, 
                        message="Data structure follows reference structure.")

        return error_detected