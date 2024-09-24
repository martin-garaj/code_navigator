_INFO = 0
_WARNING = 1
_ERROR = 2

def log_branch_report(log:list, importance:int, branch:list, message:str, message_limit:int=240):

    # get branch in dot-format with list indexing
    branch_str = ""
    for insternode in branch:
        if isinstance(insternode, int):
            branch_str = branch_str + f"[{insternode}]"
        else:
            if branch_str == "":
                branch_str = branch_str + f"{insternode}"
            else:
                branch_str = branch_str + f".{insternode}"

    _message = branch_str + f" : {message}"
    if len(_message) > message_limit and message_limit > 5:
        _message = _message[0:(message_limit-4)] + ' ...'
    log.append({"importance":importance, "message":_message})

    return log


def log_report(log:list, importance:int, message:str, message_limit:int=240):
    
    if len(_message) > message_limit and message_limit > 5:
        _message = _message[0:(message_limit-4)] + ' ...'
    log.append({"importance":importance, "message":message})
    
    return log