import os
from pathlib import Path
from pygments.lexers import get_lexer_by_name
import re
from typing import Union, Tuple, List, Any, Generator
import yaml


from python_lib.log import print_report, _CRITICAL


## ========================================================================== ##
##                                    UTILS                                   ##
## ========================================================================== ##

## ===================== get_line_number_from_permalink ===================== ##
def get_line_number_from_permalink(
        permalink:str, 
        pattern:str=r'#L(\d+)$', 
        default_line_number:int=1,
    ) -> int:
    # default value
    line_number = default_line_number
    # get number from git-permalink
    # https://github.com/.../inference.py#L13 -> yields 13
    if isinstance(permalink, str):
        match = re.search(pattern, permalink)
        if match:
            try:
                line_number = int(match.group(1))
            except:
                pass
    
    return line_number


## ====================== check_valid_syntax_highlight ====================== ##
def check_valid_syntax_highlight(syntax_highlight:str):
    try:
        _ = get_lexer_by_name(syntax_highlight, stripall=True)
    except Exception as e:
        return False
    return True


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


## ============================ get_files_of_type =========================== ##
def get_files_of_type(folder_path, file_extension, recursive):
    folder_path = Path(folder_path)
    file_paths = []
    
    if not isinstance(file_extension, list):
        file_extension = [file_extension]

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            for _extention in file_extension:
                if file.endswith(_extention):
                    file_paths.append(Path(root).joinpath(file))
                break
        if not recursive:
            break
    return file_paths


## ============================= load_yaml_file ============================= ##
def load_yaml_file(file_path:str):
    try:
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
    except Exception as e:
        print_report(
            importance=_CRITICAL, 
            message=\
                f"Exception when reading/parsing file '{file_path}': {e}")
        raise RuntimeError(\
            f"Exception when reading/parsing file '{file_path}': {e}")
    return data