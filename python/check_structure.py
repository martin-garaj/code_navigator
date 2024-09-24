from log import log_branch_report, log_report, _INFO, _WARNING, _ERROR
from typing import Union, Tuple, List, Any, Generator, Dict


## ========================= _iterate_over_structure ======================== ##
def _iterate_over_structure(
        structure: Union[dict, list], 
        member_list:list=None,
    ) -> Generator[Tuple[List[Union[str, int]], Any], None, None]:
    """ Recursive function that yields `branch` and `leaf` value from a 
    provided `structure`.

    :param structure: Nested structure represented by `dict` and `list`. 
        Notice, `list` where items are not `dict` or `list` 
        is reported as leaf (the iteration stops), includes empty list.
    :param member_list: List of members traversed to return `leaf` value, 
        defaults to None
    :yield: Yields list of members and leaf value.
    """
    if member_list is None:
        member_list = []

    if isinstance(structure, dict):
        for key, item in structure.items():
            new_member_list = member_list + [key]
            yield from _iterate_over_structure(
                    structure=item, 
                    member_list=new_member_list,
                )

    if isinstance(structure, list):
        # `list` can be a `leaf`` that has no nesting 
        # (no `dict` or `list` members), rather the list is the final leaf
        if len(structure) == 0:
            yield (member_list, structure)
        elif not isinstance(structure[0], list) and \
             not isinstance(structure[0], dict):
            yield (member_list, structure)
        else:
            for index, item in enumerate(structure):
                new_member_list = member_list + [index]
                yield from _iterate_over_structure(
                        structure=item, 
                        member_list=new_member_list,
                    )

    if not isinstance(structure, (dict, list)):
        yield (member_list, structure)

## ============================ flatten_hierarchy =========================== ##
def flatten_hierarchy(
        structure: Union[dict, list],
    ) -> List[Tuple[List[Union[str, int]], Any]]:
    """ Given a nested structure returns a list of tuples. The first element 
    of tuple is `branch` (list of structure members) that leads to `leaf` 
    (the value stored at the end of the branch).

    :param structure: Nested structure represented by `dict` and `list`. 
        Notice, `list` where items are not `dict` or `list` 
        is reported as leaf (the iteration stops), includes empty list.
    :return: List of Tuples, each tuple includes `branch` and `leaf`.
    """
    hierarchy = []
    for (member_list, value) in _iterate_over_structure(structure=structure):
        hierarchy.append((member_list, value))
    return hierarchy


## ============================== verify_branch ============================= ##
def verify_branch(
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


## ========================= check_data_consistency ========================= ##
def check_data_consistency(
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
    log = []
    flat_hierarchy = flatten_hierarchy(structure=data)
    no_warnings_or_errors = True

    for branch, value in flat_hierarchy:
        if value is None:
            log = log_branch_report(
                    log=log, 
                    importance=_WARNING, 
                    branch=branch, 
                    message="branch contains no content.",
                )
            no_warnings_or_errors = False
        else:
            exists, valid_internodes, invalid_internode = verify_branch(
                    branch=branch, 
                    reference=reference,
                )
            if not exists:
                log = log_branch_report(
                        log=log, 
                        importance=_ERROR, 
                        branch=valid_internodes+[invalid_internode], 
                        message=\
                                f"branch has invalid member "\
                                f"'{invalid_internode}', contains '{value}'"\
                            )
                no_warnings_or_errors = False
    if no_warnings_or_errors:
            log_report(log=log, importance=_INFO, 
                       message="No warning or errors detected.")
    return log


## ========================================================================== ##
##                                    TEST                                    ##
## ========================================================================== ##
if __name__ == "__main__":

    import yaml
    import json

    config_path = r'./config.yaml'

    with open(config_path, 'r') as file:
        config_file = yaml.safe_load(file)

    file_path = r'./data_to_explore/_example_.yaml'
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)


    print(json.dumps(data, indent=4))

    reference = config_file['dataStructure']

    # flat_hierarchy = flatten_hierarchy(structure=data)

    log = check_data_consistency(
        data=data, 
        reference=reference,
    )

    # print report
    for report in log:
        if report['importance'] == _INFO:
            print(f"   INFO    : {report['message']}")
        if report['importance'] == _WARNING:
            print(f"   WARNING : {report['message']}")
        if report['importance'] == _ERROR:
            print(f"---ERROR---: {report['message']}")

