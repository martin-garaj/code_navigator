# global variable
_PREPEND_TO_REPORT = ""

_NOTE = 0     # just a note on process
_WARNING = 1  # something is not as expected, but generated HTML will work
_ERROR = 2    # cannot be skipped, will eventually fail during runtime
_CRITICAL = 3 # cannot be skipped, always fail to generate HTML


def log_set_prepend(value, max_len:int=None):
    global _PREPEND_TO_REPORT
    if max_len is None:
        max_len = 0
    _PREPEND_TO_REPORT = f"{str(value).ljust(max_len)} "

    
    
def log_reset_prepend():
    global _PREPEND_TO_REPORT
    _PREPEND_TO_REPORT = ""


def log_branch_report(log:list, 
                      importance:int, 
                      branch:list, 
                      message:str, 
                      message_limit:int=240,
                    ):

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
    
    if len(message) > message_limit and message_limit > 5:
        message = message[0:(message_limit-4)] + ' ...'
    log.append({"importance":importance, "message":message})
    
    return log


def print_report(importance:int, message:str, message_limit:int=240):
    log = []
    log = log_report(
            log=log, 
            importance=importance, 
            message=message, message_limit=message_limit)
    print_log(log, min_importance=_NOTE)


def print_log(log, min_importance:int):
    global _PREPEND_TO_REPORT
    for report in log:
        if report['importance'] >= min_importance:
            if report['importance'] == _NOTE:
                report_str = \
                    f"{_PREPEND_TO_REPORT}message  : {report['message']}"
            elif report['importance'] == _WARNING:
                report_str = \
                    f"{_PREPEND_TO_REPORT}warning  : {report['message']}"
            elif report['importance'] == _ERROR:
                report_str = \
                    f"{_PREPEND_TO_REPORT}ERROR    : {report['message']}"
            elif report['importance'] == _CRITICAL:
                report_str = \
                    f"{_PREPEND_TO_REPORT}CRITICAL : {report['message']}"
            else:
                report_str = \
                    f"{_PREPEND_TO_REPORT}---------: {report['message']}"
            print(report_str)
            
            
# auxiliary functions
def print_headline(headline:str, fill:str='-', width:int=80):
    """ Print nicely formatted header.
    
        #================== ... ==================#
        =                <headline>               =
        #================== ... ==================#

    :param headline: _description_
    :param fill: _description_, defaults to '-'
    :raises ValueError: _description_
    """
    global _PREPEND_TO_REPORT
    if len(fill) != 1:
        raise ValueError(
            f"`fill' nedds to include a single symbol, "\
            f"but includes '{fill}'")
    filler = fill * (width-2-len(_PREPEND_TO_REPORT))
    spaces_to_center = (width-2)-len(headline)-len(_PREPEND_TO_REPORT)
    if spaces_to_center % 2 == 0:
        spaces_left = int(spaces_to_center/2) * " "
        spaces_right = int(spaces_to_center/2) * " "
    else:
        spaces_left = int((spaces_to_center-1)/2) * " "
        spaces_right = int((spaces_to_center+1)/2) * " "
    print(f"{_PREPEND_TO_REPORT}#{filler}#")
    print(f"{_PREPEND_TO_REPORT}{fill}{spaces_left}{headline}{spaces_right}{fill}")
    print(f"{_PREPEND_TO_REPORT}#{filler}#")
    
    
def print_notice(notice:str, fill:str='#', width:int=80):
    if len(fill) != 1:
        raise ValueError(
            f"`fill' nedds to include a single symbol, "\
            f"but includes '{fill}'")
    global _PREPEND_TO_REPORT
    spaces_to_center = (width-4)-len(notice)-len(_PREPEND_TO_REPORT)
    if spaces_to_center % 2 == 0:
        spaces_left = int(spaces_to_center/2) * fill
        spaces_right = int(spaces_to_center/2) * fill
    else:
        spaces_left = int((spaces_to_center-1)/2) * fill
        spaces_right = int((spaces_to_center+1)/2) * fill
    print(f"{_PREPEND_TO_REPORT}{fill}{spaces_left} {notice} {spaces_right}{fill}")