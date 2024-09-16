from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
import re
import os
from pathlib import Path

from typing import List, Tuple
import yaml
import copy

import argparse
import sys

## ========================================================================== ##
##                                   CONSTS                                   ##
## ========================================================================== ##
# CSS classes
_HTML_PAGE = "page"
_HTML_PAGE_HEADER = "page-header"
_HTML_PAGE_CONTENT = "page-content"

_HTML_HEADER_TITLEPREFIX = "header-title-prefix"
_HTML_HEADER_TITLE = "header-title"
_HTML_HEADER_PERMALINK = "header-permalink"
_HTML_SECTION = "section"
_HTML_SECTION_HEADER = "section-header"
_HTML_SECTION_CONTENT = "section-content"
_HTML_PERMALINK = "permalink"

_LINK_SEARCH_PREFIX = ">"
_LINK_SEARCH_SUFFIX = "<"

_NOTE = 0
_WARNING = 1
_ERROR = 2

_FILE_SUFFIX = ".html"

## ========================================================================== ##
##                                    UTILS                                   ##
## ========================================================================== ##
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


def check_valid_syntax_highlight(syntax_highlight:str):
    try:
        _ = get_lexer_by_name(syntax_highlight, stripall=True)
    except Exception as e:
        return False
    return True


def print_headline(headline:str, fill:str='-', width:int=80):
    """ Print nicely formatted header.
    
        #================== ... ==================#
        =                <headline>               =
        #================== ... ==================#

    :param headline: _description_
    :param fill: _description_, defaults to '-'
    :raises ValueError: _description_
    """
    if len(fill) != 1:
        raise ValueError(
            f"`fill' nedds to include a single symbol, "\
            f"but includes '{fill}'")
    filler = fill * (width-2)
    spaces_to_center = (width-2)-len(headline)
    if spaces_to_center % 2 == 0:
        spaces_left = int(spaces_to_center/2) * " "
        spaces_right = int(spaces_to_center/2) * " "
    else:
        spaces_left = int((spaces_to_center-1)/2) * " "
        spaces_right = int((spaces_to_center+1)/2) * " "
    print(f"#{filler}#")
    print(f"{fill}{spaces_left}{headline}{spaces_right}{fill}")
    print(f"#{filler}#")
    
    
## ========================================================================== ##
##                             YamlConfigChecker                              ##
## ========================================================================== ##
class YamlConfigChecker:
    def __init__(self, config:dict):
        self.report = []
        self.config = config
        self.done = False
        self.valid = False

    def print_report(self) -> None:
        if not self.done:
            self.valid = self._run_check()
            self.done = True
        for line in self.report:
            if line['importance'] == _NOTE:
                line_str = f"message : {line['content']}"
            elif line['importance'] == _WARNING:
                line_str = f"WARNING : {line['content']}"
            elif line['importance'] == _ERROR:
                line_str = f"ERROR   : {line['content']}"
            else:
                line_str = f"--------: {line['content']}"
            print(line_str)


    def is_valid(self) -> bool:
        if not self.done:
            self.valid = self._run_check()
            self.done = True
        return self.valid

    def _run_check(self):

        valid = True
        # check `default` members
        default = self.config.get('default', None)
        if default is None:
            message = {
            'importance': _ERROR,
            'content': \
            f"Missing member for `config.default`, "\
            f"member is compulsory with compulsory sub-members "\
            f"`syntaxHighlight`, `pygmentsStyle`!"\
            }
            self.report.append(message)
            valid = False
        else:
            # check `default.syntaxHighlight` member
            default_syntax_highlight = default.get('syntaxHighlight', None)
            if default_syntax_highlight is None:
                message = {
                'importance': _ERROR,
                'content': \
                f"Missing member for `config.default`, member is compulsory!"\
                }
                self.report.append(message)
                valid = False
            elif not check_valid_syntax_highlight(
                syntax_highlight=default_syntax_highlight,
                ):
                message = {
                'importance': _ERROR,
                'content': \
                f"Incorrect value for `config.default.syntaxHighlight = "\
                f"'{default_syntax_highlight}'`, correct value available at "\
                f"https://pygments.org/docs/lexers/ ."\
                }
                self.report.append(message)
                valid = False
            # check `default.pygmentsStyle` member
            default_pygments_style = default.get('pygmentsStyle', None)
            if default_pygments_style is None:
                message = {
                'importance': _ERROR,
                'content': \
                f"Missing member for `config.default.pygmentsStyle`, "\
                f"member is compulsory, valid values available at "\
                f"https://dt.iki.fi/pygments-gallery ."\
                }
                self.report.append(message)
                valid = False

        # check `display` members
        display = self.config.get('display', None)
        if display is None:
            message = {
            'importance': _ERROR,
            'content': \
            f"Missing member for `config.display`, "\
            f"member is compulsory with compulsory sub-members "\
            f"`debounceTime`, `pathData`, `initFile`!"\
            }
            self.report.append(message)
            valid = False
        else:
            # check `display.debounceTime` member
            display_debounce_time = display.get('debounceTime', None)
            if display_debounce_time is None:
                message = {
                'importance': _ERROR,
                'content': \
                f"Missing member for `config.display`, member is compulsory!"\
                }
                self.report.append(message)
                valid = False
            else:
                if display_debounce_time < 0 or display_debounce_time >= 2000:
                    message = {
                    'importance': _ERROR,
                    'content': \
                    f"Incorrect value for `config.display.debounceTime`, "\
                    f"valid values `0 <= debounceTime <= 2000`!"\
                    }
                    self.report.append(message)
                    valid = False
            # check `display.debounceTime` member
            display_path_data = display.get('pathData', None)
            if display_path_data is None:
                message = {
                'importance': _ERROR,
                'content': \
                f"Missing member for `config.display.pathData`, "\
                f"member is compulsory!"\
                }
                self.report.append(message)
                valid = False
            else:
                try:
                    if not Path(__file__).parent.joinpath(\
                        display_path_data).exists():
                        path_str = str(Path(__file__).parent.joinpath(\
                            display_path_data))
                        message = {
                        'importance': _ERROR,
                        'content': \
                        f"Incorrect value for `config.display.pathData`, "\
                        f"full path is invalid: '{path_str}'!"\
                        }
                        self.report.append(message)
                        valid = False
                except Exception as e:
                    message = {
                    'importance': _ERROR,
                    'content': \
                    f"Error checking path for `config.display.pathData`: "\
                    f"{str(e)}"\
                    }
                    self.report.append(message)
                    valid = False

            # check `display.initFile` member
            display_init_file = display.get('initFile', None)
            if display_init_file is None:
                message = {
                'importance': _ERROR,
                'content': \
                f"Missing member for `config.display.initFile`, "\
                f"member is compulsory!"\
                }
                self.report.append(message)
                valid = False
                # DO NOT control the path, there is not reason the 'initFile' 
                # exists at the time of config check    
        # check `performance` members
        performance = self.config.get('performance', None)
        if performance is None:
            message = {
            'importance': _ERROR,
            'content': \
            f"Missing member for `config.performance`, "\
            f"member is compulsory with compulsory sub-member "\
            f"`loggingTime`!"\
            }
            self.report.append(message)
            valid = False
        else:
            # check `performance.debounceTime` member
            display_logging_time = performance.get('loggingTime', None)
            if display_logging_time is None:
                message = {
                'importance': _ERROR,
                'content': \
                f"Missing member for `config.performance.loggingTime`, "\
                f"member is compulsory!"\
                }
                self.report.append(message)
                valid = False
            else:
                if display_logging_time < 1000:
                    message = {
                    'importance': _ERROR,
                    'content': \
                    f"Incorrect value for `config.performance.loggingTime`, "\
                    f"valid value `loggingTime >= 1000`!"\
                    }
                    self.report.append(message)
                    valid = False

        return valid


## ========================================================================== ##
##                              YamlDataChecker                               ##
## ========================================================================== ##
class YamlDataChecker:
    def __init__(self, yaml:dict, config:dict, drop_invalid:bool=False):
        self.report = []
        self.config_data_path = config['display']['pathData']
        self.config_default_syntax_highlight = config['default']['syntaxHighlight']
        self.yaml = yaml
        self.drop_invalid = drop_invalid

        self.done = False
        self.valid = None
        

    def is_valid(self) -> bool:
        if not self.done:
            self.valid = self._run_check()
            self.done = True
        return self.valid


    def print_report(self) -> None:
        if not self.done:
            self.valid = self._run_check()
            self.done = True
        for line in self.report:
            if line['importance'] == _NOTE:
                line_str = f"message : {line['content']}"
            elif line['importance'] == _WARNING:
                line_str = f"WARNING : {line['content']}"
            elif line['importance'] == _ERROR:
                line_str = f"ERROR   : {line['content']}"
            else:
                line_str = f"--------: {line['content']}"
            print(line_str)


    def _run_check(self) -> bool:
        self.report = []
        if isinstance(self.yaml, type(None)):
            self.done = True
            self.valid = False
            message = {
            'importance': _ERROR,
            'content': f"Yaml file is empty."
            }
            self.report.append(message)
            return self.valid
            
        valid_header = self.check_yaml_header(
                header=self.yaml.get('header', None),
            )
        valid_sections, list_of_sections = self.check_yaml_sections(
            sections=self.yaml.get('sections', None),
            )
        self.yaml['sections'] = list_of_sections

        self.valid = valid_header and valid_sections
        return self.valid


    def check_yaml_sections(self, sections:list) -> List[dict]:
        list_of_sections = []
        valid_sections = True
        if sections is None:
            message = {
            'importance': _WARNING,
            'content': f"Missing member for `yaml.sections`, "\
                f"no content will be displayed except title."
            }
            self.report.append(message)
        else:
            for section_index, section in enumerate(sections):
                valid_header, valid_content, list_of_valid_links = \
                    self.check_yaml_section(
                            section=section, 
                            section_index=section_index, 
                        )

                # check if dropping
                if self.drop_invalid:
                    if valid_header and valid_content:
                        # preserve only valid sections with only valid links
                        _section = copy.deepcopy(section)
                        _section['links'] = list_of_valid_links
                        list_of_sections.append(_section)
                    else:
                        # do not preserve
                        message = {
                        'importance': _WARNING,
                        'content': \
                        f"Dropping `yaml.sections[{section_index}]` "\
                        f"due to reasons above related "\
                        f"to this section and `drop_invalid=True` setting!"
                        }
                        self.report.append(message)
                else:
                    # preserve all links
                    list_of_sections.append(section)
            valid_sections = valid_sections and (valid_header and valid_content)
        return valid_sections, list_of_sections


    def check_yaml_header(self, header) -> None:
        """ Check `header` member of yaml file .
        """
        valid_header = True
        if header is None:
            message = {
                'importance': _ERROR,
                'content': \
                    f"Missing `yaml.header` but `header` is compulsory!",
            }
            self.report.append(message)
            valid_header = False
        else:
            if 'title' not in header.keys():
                message = {
                    'importance': _ERROR,
                    'content': f"Missing member `yaml.header.title`, "\
                    f"but `title` is compulsory!",
                }
                self.report.append(message)
                valid_header = False
            elif header['title'] == None:
                message = {
                    'importance': _ERROR,
                    'content': f"Missing value for `yaml.header.title = ''`, "\
                    f"but `title` is compulsory!",
                }
                self.report.append(message)
                valid_header = False
        return valid_header


    def check_section_link_matchstring(
                self, 
                link:dict, 
                section_index:int, 
                link_index:int,
            ) -> bool:
        valid_link = True
        if 'matchString' not in link.keys():
            message = {
                'importance': _ERROR,
                'content': \
                f"Missing member `yaml.sections[{section_index}]."\
                f"links[{link_index}].matchString` but "\
                f"`matchString` is compulsory!",
            }
            self.report.append(message)
            valid_link = False
        elif link['matchString'] == None:
            message = {
                'importance': _ERROR,
                'content': \
                f"Missing value for `yaml.sections[{section_index}]."\
                f"links[{link_index}].matchString = ''`, "\
                f"matchString cannot be empty, valid values: "\
                f"1) empty [], "\
                f"2) only positive including `0` [0, 2], "\
                f"3) only negative [-2 -5]",
            }
            self.report.append(message)
            valid_link = False
        return valid_link
    

    def check_section_link_linkfile(
                self, 
                link:dict, 
                section_index:int, 
                link_index:int,
            ) -> bool:
        valid_linkfile = True
        if 'linkFile' not in link.keys():
            message = {
                'importance': _ERROR,
                'content': \
                f"Missing member `yaml.sections[{section_index}]."\
                f"links[{link_index}].linkFile` but "\
                f"`linkFile` is compulsory!",
            }
            self.report.append(message)
            valid_linkfile = False
        elif link['linkFile'] == None:
            message = {
                'importance': _ERROR,
                'content': \
                f"Missing value for `yaml.sections[{section_index}]."\
                f"links[{link_index}].linkFile = ''`, but "\
                f"`linkFile` is compulsory!",
            }
            self.report.append(message)
            valid_linkfile = False
        else:
            try:
                if not Path(__file__).parent.joinpath(\
                    self.config_data_path, link['linkFile']).exists():
                    path_str = str(Path(__file__).parent.joinpath(\
                        self.config_data_path, link['linkFile']))
                    message = {
                        'importance': _WARNING,
                        'content': \
                        f"File path `yaml.sections[{section_index}]."\
                        f"links[{link_index}].linkFile = '{path_str}'` is not valid, "\
                        f"assure the file exists to avoid runtime errors "\
                        f"(config.display.dataPath = '{self.config_data_path}')!",
                    }
                    self.report.append(message)
            except Exception as e:
                message = {
                    'importance': _ERROR,
                    'content': \
                    f"Error checking path for `yaml.sections[{section_index}]."\
                    f"links[{link_index}].linkFile`: {str(e)}",
                }
                self.report.append(message)
        return valid_linkfile


    def check_section_link_matchindex(
                self, 
                link:dict, 
                section_index:int, 
                link_index:int,
            ) -> bool:
        
        valid_matchindex = True
        if link['matchIndex'] == None:
            message = {
                'importance': _ERROR,
                'content': \
                f"Missing member `yaml.sections[{section_index}]."\
                f"links[{link_index}].matchIndex` but "\
                f"`matchIndex` is compulsory!",
            }
            self.report.append(message)
            valid_matchindex = False
        elif not self.check_matchindex_value(link['matchIndex']):
            message = {
                'importance': _ERROR,
                'content': \
                f"Incorrect value for member `yaml.sections[{section_index}]."\
                f"links[{link_index}].matchIndex = {link['matchIndex']}`, "\
                f"valid values: "\
                f"1) empty [], "\
                f"2) only positive including `0` [0, 2], "\
                f"3) only negative [-2 -5]"
            }
            self.report.append(message)
            valid_matchindex = False
        return valid_matchindex


    def check_yaml_section_link(
            self, 
            link:dict, 
            section_index:int, 
            link_index:int,
            ):
        # check compulsory fields
        valid_matchstring = self.check_section_link_matchstring(
                link=link, 
                section_index=section_index, 
                link_index=link_index,
            )
        valid_linkfile = self.check_section_link_linkfile(
                        link=link, 
                        section_index=section_index, 
                        link_index=link_index,
                    )
        valid_link = valid_matchstring and valid_linkfile
        return valid_link

    def check_yaml_section_content(
                self, 
                content:dict,
                section_index:int, 
            ) -> bool:
        valid_content = True
        # check `content`
        if content is None:
            message = {
                'importance': _ERROR,
                'content': \
                f"Missing member `yaml.sections[{section_index}].content`, "\
                f"but it is compulsory!"
            }
            self.report.append(message)
            valid_content = False 
        else:
            # check `syntaxHighlight`
            syntax_highlight = content.get('syntaxHighlight', None)
            if syntax_highlight is not None:
                if not check_valid_syntax_highlight(
                        syntax_highlight=syntax_highlight,
                    ):
                    valid_content = False
                    message = {
                        'importance': _WARNING,
                        'content': \
                        f"Incorrect `yaml.sections[{section_index}].content."\
                        f"syntaxHighlight = '{syntax_highlight}'`, "\
                        f"default value "\
                        f"'{self.config_default_syntax_highlight}'"
                    }
                    self.report.append(message)
            # check `text`
            text = content.get('text', None)
            if text is None:
                message = {
                    'importance': _ERROR,
                    'content': \
                    f"Missing member for `yaml.sections[{section_index}]."\
                    f"content.text`, "\
                    f"but it is compulsory!"
                }
                self.report.append(message)
                valid_content = False
            elif not isinstance(text, str):
                message = {
                    'importance': _ERROR,
                    'content': \
                    f"Incorrect type for `yaml.sections[{section_index}]."\
                    f"content.text = <{type(text)}>`, but <str> is required!"
                }
                self.report.append(message)
                valid_content = False
        return valid_content


    def check_yaml_section(
            self, 
            section:dict, 
            section_index:int, 
            ) -> Tuple[bool, bool, List[dict]]:
        # check section header
        valid_header = self.check_yaml_header(
                header=section.get('header', None),
            )
        valid_content = self.check_yaml_section_content(
                content=section.get('content', None),
                section_index=section_index, 
            )
        # links are optional
        list_of_valid_links = []
        links = section.get('links', None)
        if links is not None:
            # check `matchStrings`
            matchStrings = []
            for link_index, link in enumerate(links):
                valid_link = self.check_yaml_section_link(
                            link=link, 
                            section_index=link_index, 
                            link_index=link_index,
                        )
                # if `valid_link==True`, check for duplicates
                if valid_link:
                    if link['matchString'] not in matchStrings:
                        matchStrings.append(link['matchString'])
                    else:
                        # link is duplicate, invalidate link
                        valid_link = False
                        message = {
                        'importance': _ERROR,
                        'content': \
                        f"Duplicate value for `yaml.sections[{section_index}]."\
                        f"links[{link_index}].matchIndex = "\
                        f"{link['matchIndex']}`, with previously checked "\
                        f"links[{matchStrings.index(link['matchString'])}]."
                        }
                        self.report.append(message)
                # check if dropping
                if self.drop_invalid:
                    if valid_link:
                        # preserve only valid links
                        list_of_valid_links.append(link)
                    else:
                        # do not preserve
                        message = {
                        'importance': _WARNING,
                        'content': \
                        f"Dropping `yaml.sections[{section_index}]."\
                        f"links[{link_index}]` due to reasons above related "\
                        f"to this link and `drop_invalid=True` setting!"
                        }
                        self.report.append(message)
                else:
                    # preserve all links
                    list_of_valid_links.append(link)
        return valid_header, valid_content, list_of_valid_links


    def check_matchindex_value(self, match_index:list) -> str:
        """ This function is closely tied to `check_index_within_match_index()`, 
            see *Interpretation*. Returns True if `match_index` is correct, 
            False otherwise.

        :param match_index: List of indices.
        :return: Report on possible erros.
        """
        if len(match_index) == 0:
            return True
        if match_index[0] >= 0:
            for index in match_index:
                if index < 0:
                    return False
        if match_index[0] < 0:
            for index in match_index:
                if index >= 0:
                    return False
        return True


## ========================================================================== ##
##                                    HTML                                    ##
## ========================================================================== ##

class YamlToHtml():

    def __init__(self, yaml:dict, config:dict, suffix:str=".html"):
        self.yaml = yaml
        self._default_syntax_highlight = config['default']['syntaxHighlight']
        self.suffix = suffix
        self.report = []
        self._html_page = ""
        self.done = False

    @property
    def html_page(self):
        if not self.done:
            self.generate_html_page()
        return self._html_page

    ## ============================= _log_report ============================ ##
    def _log_report(self, importance:int, content:str):
        if importance not in [_NOTE, _WARNING, _ERROR]:
            raise ValueError(
                f'`importance` has undefined value `{importance}`, '\
                f'valid values [{_NOTE}, {_WARNING}, {_ERROR}]')
        self.report.append({'importance':importance, 'content': content})


    ## ============================ print_report ============================ ##
    def print_report(self) -> None:
        if not self.done:
            self.valid = self._run_check()
            self.done = True
        for line in self.report:
            if line['importance'] == _NOTE:
                line_str = f"message : {line['content']}"
            elif line['importance'] == _WARNING:
                line_str = f"WARNING : {line['content']}"
            elif line['importance'] == _ERROR:
                line_str = f"ERROR   : {line['content']}"
            else:
                line_str = f"--------: {line['content']}"
            print(line_str)
            
            
    ## ========================= generate_html_page ========================= ##
    def generate_html_page(self) -> None:
        """ Generate HTML document from header and sections.
        """
        # header
        header = self.yaml.get('header', None)
        html_header = self.create_html_header(
                header=header, 
                css_class_list=[],
            )
        # sections
        sections = self.yaml.get('sections', [])
        html_sections = ""
        for section in sections:
            html_section = self.create_html_section(section=section)
            html_sections += html_section

        html_page = \
            f'<div class="{_HTML_PAGE}">\n' \
                f'<script type="application/json" id="page-data">\n' \
                    f'{"{"}"pageTitle": "{header.get("title", None)}"{"}"}\n' \
                f'</script>\n' \
                f'<div class="{_HTML_PAGE_HEADER}">\n' \
                    f'{html_header}' \
                f'</div>\n' \
                f'<div class="{_HTML_PAGE_CONTENT}">\n' \
                    f'{html_sections}' \
                f'</div>\n' \
            f'</div>\n'

        self._html_page = html_page
        self.done = True


    ## =========================== highlight_text =========================== ##
    def highlight_text(self, 
                       text:str, 
                       syntax_highlight:str, 
                       include_line_numbers:bool, 
                       line_number_start:int=1,
                    ) -> str:
        """ Highlight syntax using Pygments HtmlFormatter.

        :param text: String representing the text to be highlighted
        :param syntax_highlight: Syntax highlight alias (e.g. cpp)
        :return: Highlighted HTML text using Pygments Lexer 
        """
        lexer = get_lexer_by_name(syntax_highlight, stripall=True)
        formatter = HtmlFormatter(
                linenostart=line_number_start,
                linenos=include_line_numbers, #'table' if include_line_numbers else False,
                full=False, # do not include CSS 
            )
        highlighted_text = highlight(text, lexer, formatter)
        return highlighted_text


    ## ======================= create_whole_word_regex ====================== ##
    def create_whole_word_regex(self, 
                                word:str, 
                                prefix:str='', 
                                suffix:str='',
                            ):
        """ Returns a regex expression that matches *whole* words only.

        *Example*
        `searched_string = 
            "
            line 1: var_word_(int)
            line 2: var_word_extended
            line 3: var_word_-3
            line 4: _word_
            "`
        `word="_word_"`
        Regex expression in this function needs to return line 4 only.

        :param word: String to match, e.g. "_word_", "2+2"
        :return: Regex expression matching whole-word expressions
        """
        word = prefix+word+suffix
        return rf'(?<![a-zA-Z0-9_])({re.escape(word)})(?![a-zA-Z0-9_])'

    ## =================== check_index_within_match_index =================== ##
    def check_index_within_match_index(self, 
                                       index:int, 
                                       match_index:List[int],
                                    ) -> bool:
        """ This function defines the logic for interpreting the values within 
            'matchIndex' from yaml. 

            *Interpretation*
            The *interpretation* is an important term, since there is no default 
            interpretation of e.g. `match_index==[]`, 
            or e.g. `match_index[0]=-1`.
            This function interprets the *match* according to these rules:
            - `match_index==[]` returns always True for any value of `index`
            - `match_index==[2]` returns True if `index==2`, otherwise False
            - `match_index==[-2]` returns False if `index==2`, otherwise True

            *Invalid case*
            The following case is not interpretable.
            - `match_index==[0, -2]`
            The reason is that `0` is a selector for positive cases 
            (return True, otherwise False), while `-2` is used for negative 
            cases (return False, otherwise True). But if the `0` is included 
            then the value `-2` is either redundant OR it is an error, since 
            `match_index==[0]` would behave the same as `match_index==[0, -2]`, 
            thus this case is not interpretable OR an error.
    
        :param index: Current index value.
        :param match_index: List of indices that *match* the `index` value.
        :return: True if *match*, False if no *match* (see *Interpretation*)
        """
        if len(match_index) == 0:
            return True
        
        if match_index[0] >= 0:
            if index in match_index:
                return True
            else:
                return False
            
        if match_index[0] < 0:
            if -index in match_index:
                return False
            else:
                return True


    ## ============================= create_link ============================ ##
    def create_link(self,
                match_string:str, 
                link_file:str, 
                section_tag:str=None, 
                css_class:str=None,
            ) -> str:
        """ Format link string that encapsulates the calls to javascript 
            functions and HTML attributes to contain necessary information.

        :param match_string: String to match inside highlighted code
        :param link_file: file to link (relative path)
        :param section_tag: _description_
        :param css_class: _description_
        :return: _description_
        """
        link_file = link_file + self.suffix
        link = f"<a "
        if section_tag is not None:
            link += f"section-tag='{section_tag}' "
        link += f"onclick=\"handleClick('{match_string}', '{link_file}')\" "\
                f"onmouseover=\"debouncedHandleHover('{link_file}')\" "
        if css_class is not None:
            link += f"class=\"{_HTML_PERMALINK} {css_class}\""
        else:
            link += f"class=\"{_HTML_PERMALINK}\""
        link += f">{match_string}</a>"

        return link


    ## =================== insert_link_to_highlighted_code ================== ##
    def insert_link_to_highlighted_code(
            self,
            highlighted_code:str, 
            match_string:str, 
            match_index:List[int],
            link:str) -> Tuple[str, int]:
        """ Replace `match_string` with `link` within `highlighted_code` (HTML) 
            according to logic provided throug `match_index`.

        :param highlighted_code: String representing highlighted code.
        :param match_string: String to be replaced by `link`.
        :param match_index: List of indices where the insertion is 
            ignored/allowed (see *Interpretation* within 
            `check_index_within_match_index()`)
        :param link: String representing HTML tag that replaces the 
            `match_string`.
        :return: Returns highlighted code (HTML) with inserted HTML tags 
            representing the links.
        """
        pattern = self.create_whole_word_regex(
                word=match_string, 
                prefix=_LINK_SEARCH_PREFIX, 
                suffix=_LINK_SEARCH_SUFFIX,
            )
        result = []
        last_end = 0
        match_count = 0

        while True:
            match = re.search(pattern, highlighted_code[last_end:])
            if not match:
                result.append(highlighted_code[last_end:])
                break

            start, end = match.span()
            result.append(highlighted_code[last_end:(last_end+start)])

            if self.check_index_within_match_index(
                    index=match_count, 
                    match_index=match_index,
                ):
                result.append(_LINK_SEARCH_PREFIX+link+_LINK_SEARCH_SUFFIX)
            else:
                result.append(match.group(1))

            last_end += end
            match_count += 1

        return ''.join(result), match_count


    ## =================== insert_link_to_highlighted_code ================== ##
    def create_html_header(self, 
                           header:dict, 
                           css_class_list:List[str]=[],
                        ) -> str:
        """ Returns an HTML string representing header.

            *Example*
                header.titlePrefix = /llama.cpp/
                header.title = simple.cpp
                header.permalink = URL
            yields
                /llama.cpp/simple.cpp [permalink]

        :param header: Dictionary with optional keys: 'titlePrefix', 'title', 
            'permalink'
        :param css_class_list: List of CSS classes assigned to HTML, 
            defaults to []
        :return: HTML string
        """
        header_html = ""
        css_classes = ' '.join(css_class_list)
        if len(css_classes) > 0:
            css_classes = ' '+css_classes
        title_prefix = header.get('titlePrefix', None)
        if title_prefix is not None:
            header_html += \
                f'<span class="{_HTML_HEADER_TITLEPREFIX}{css_classes}">'\
                f'{title_prefix}</span>\n'
        title = header.get('title', None)
        if title is not None:
            header_html += \
            f'<span class="{_HTML_HEADER_TITLE}{css_classes}">{title}</span>\n'
        permalink = header.get('permalink', None)
        if permalink is not None:
            header_html += \
                f'<a href="{permalink}" target="_blank" '\
                f'class="{_HTML_HEADER_PERMALINK}{css_classes}">link</a>\n'
        return header_html


    ## =================== insert_link_to_highlighted_code ================== ##
    def create_html_section_content(
            self,
            section_text:str, 
            syntax_highlight:str, 
            include_line_numbers:bool,
            line_number_start:int=1,
        ) -> str:
        """ Processes section content composed of text that is highlighted 
            and formatted accordingly.

        :param section_text: `text` of the section
        :param syntax_highlight: Syntax highlighter passed to Pygments lexer
        :param include_line_numbers: If True, line numbers are included
        :param line_number_start: Start of line numbering, defaults to 1
        :return: HTML string representing highlighted text
        """
        if isinstance(section_text, str):
            section_text = self.highlight_text(
                    text=section_text, 
                    syntax_highlight=syntax_highlight,
                    include_line_numbers=include_line_numbers,
                    line_number_start=line_number_start,
                )
            section_text += "\n"
        else:
            section_text = ""
        return section_text

    ## ========================= create_html_section ======================== ##
    def create_html_section(
            self,
            section:dict, 
            section_index:int=0,
        ) -> str:
        """ Process section including: 
            - header - title, titlep prefix and external link
            - content - highlighted text
            - links - seraching highlighted text and injecting JS callbacks

        :param section: Dictionary representing the section structure
        :param section_index: Section index, since page contains multiple 
            indices, defaults to 0
        :return: HTML string representing section
        """
        # section header 
        section_header = section.get('header', None)
        if section_header is not None:
            section_header_html = self.create_html_header(
                    header=section_header, 
                    css_class_list=[],
                )
        else: 
            section_header_html = ''

        # section syntaxHighlight
        section_content = section.get('content', None)
        if section_content is None:
            section_highlighted_content = ""
        else:
            syntax_highlight = section_content.get('syntaxHighlight', None)
            syntax_highlight = syntax_highlight \
                                if syntax_highlight is not None \
                                else self._default_syntax_highlight
        
            # line numbers are not included for default syntaxHighlight
            include_line_numbers= \
                not (syntax_highlight==self._default_syntax_highlight)

            # section content
            section_text = section_content.get('text', None)
            section_highlighted_content = \
                self.create_html_section_content(
                    section_text=section_text, 
                    syntax_highlight=syntax_highlight,
                    include_line_numbers=include_line_numbers,
                    # line_number_start=get_line_number_from_permalink(
                    #     permalink=section_header.get('permalink', None),
                    # ),
                    # line_number_start=1,
                )

            # links
            links = section.get('links', [])
            for link_index, link in enumerate(links):
                html_link = \
                    self.create_link(
                            match_string=link.get('matchString', None), 
                            link_file=link.get('linkFile', None), 
                            section_tag=link.get('sectionTag', None), 
                            css_class=link.get('cssClass', None),
                        )
                section_highlighted_content, match_count = \
                    self.insert_link_to_highlighted_code(
                            highlighted_code=section_highlighted_content, 
                            match_string=link['matchString'], 
                            match_index=link['matchIndex'],
                            link=html_link,
                        )
                if match_count == 0:
                    self._log_report(
                        importance=_WARNING, 
                        content="")
                    report += \
                        f"No match found for '{link.get('matchString', None)}'"\
                        f" from yaml.sections[{section_index}]."\
                        f"link[{link_index}] in section `text`."
        section_html = \
            f'<div class="{_HTML_SECTION}">\n' \
                f'<div class="{_HTML_SECTION_HEADER}">\n' \
                    f'{section_header_html}' \
                f'</div>\n' \
                f'<div class="{_HTML_SECTION_CONTENT}">\n' \
                    f'{section_highlighted_content}' \
                f'</div>\n' \
            f'</div>\n'
        return section_html


## ========================================================================== ##
##                            Recursive processing                            ##
## ========================================================================== ##
def get_files_of_type(folder_path, file_extension, recursive):
    folder_path = Path(folder_path)
    file_paths = []
    
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(file_extension):
                file_paths.append(Path(root).joinpath(file))
        if not recursive:
            break
    return file_paths


## ========================================================================== ##
##                                    main                                    ##
## ========================================================================== ##
def main():
    parser = argparse.ArgumentParser(
        description=\
            f"Processes all <file_name>.yaml in process_path="\
            f"<this-script-path>/<config.display.pathData>/ into HTML files "\
            f"(<file_name>.yaml are kept untouched).")
    parser.add_argument("-d", "--directory", 
                default=str(Path(__file__).parent),
                help=f"Path to directory where the script will "\
                    f"execute (default: script's directory)")
    parser.add_argument("-r", "--recursive", 
                action="store_true",
                help=f"If set, the script enters all sub-folders.")
    parser.add_argument("-f", "--force", 
                action="store_true",
                help=f"If set, existing files will be replaced by "\
                    f"newly generated files")
    parser.add_argument("-c", "--config", 
                default=str(Path(__file__).parent.joinpath("config.yaml")),
                help=f"Path to config file "\
                    f"(default: config.yaml in script's directory)")
    args = parser.parse_args()

    # Process config argument
    if os.path.isabs(args.config):
        config = Path(args.config)
    else:
        config = Path(Path(__file__).parent.joinpath(args.config))

    if not config.exists():
        print(f"Error: The specified config file does not exist: {config}")
        sys.exit(1)
    else:
        try:
            with open(config, 'r') as file:
                config = yaml.safe_load(file)
        except Exception as e:
            print(f"Error: The specified config file cannot be parsed: {e}")
            sys.exit(1)

    # Process directory argument
    if os.path.isabs(args.directory):
        if not os.path.exists(args.directory):
            print(f"Error: The specified directory does not exist: {args.directory}")
            sys.exit(1)
        directory = Path(args.directory)
    else:
        directory = Path(Path(__file__).parent.joinpath(args.directory))
        if not directory.exists():
            print(f"Error: The specified relative directory does not exist: {directory}")
            sys.exit(1)

    # Process force argument
    force = args.force
    
    # Process recursive argument
    recursive = args.recursive

    # console output
    print_headline(headline='Inputs', fill='-', width=80)
    # You can now continue with your own code using these variables
    print(f"Directory: {directory}")
    print(f"Force:     {force}")
    print(f"Recursive: {recursive}")
    print(f"Config:    {config}")


    # Config checker
    config_checker = YamlConfigChecker(config=config)
    if not config_checker.is_valid():
        config_checker.print_report()
        sys.exit(1)

    # Add your own code here
    file_paths = get_files_of_type(
        folder_path=Path(directory, config['display']['pathData']), 
        file_extension='.yaml', 
        recursive=recursive)
    
    num_generated = 0
    num_skipped = 0
    for file_path in file_paths:
        # open file
        try:
            with open(file_path, 'r') as file:
                yaml_file = yaml.safe_load(file)
        except Exception as e:
            print(f"Error: Error when reading/parsing file '{file_path}': {e}")
            sys.exit(1)
            
        file_checker = YamlDataChecker(
            yaml=yaml_file, 
            config=config, 
            drop_invalid=False)
        
        if not file_checker.is_valid():
            print_headline(headline="Skipping file", fill="!")
            print(file_path)
            file_checker.print_report()
            del file_checker
            continue
        else:
            print_headline(headline="Processing file", fill="=")
            print(file_path)
            
        # get yaml_to_html generator
        yaml_to_html = YamlToHtml(
                yaml=yaml_file, 
                config=config, 
                suffix=_FILE_SUFFIX,
            )
        yaml_to_html.generate_html_page()
        yaml_to_html.print_report()

        # save <file_path>.html to file, check for 
        full_html_path = Path(str(file_path)+_FILE_SUFFIX)
        if full_html_path.exists() and not force:
            raise RuntimeError(
                f"ERROR: file '{str(full_html_path)}' already exists! "\
                f"Run this script again with -f/--force option to rewrite "\
                f"existing files.")
        else:
            with open(full_html_path, "w") as file:
                file.write(yaml_to_html.html_page)
            num_generated += 1
                
        # delete 
        del file_checker
        del yaml_to_html
        
    print_headline(
            headline=f'Generated {num_generated} files (skipped {num_skipped})',
            fill='#', 
            width=80,
        )
    
    
if __name__ == "__main__":
    main()









