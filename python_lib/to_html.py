from pathlib import Path
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
import re
from typing import Tuple, List


from python_lib.utils import get_line_number_from_permalink, \
    check_valid_syntax_highlight
from python_lib.log import log_branch_report, log_report, print_log, \
    _NOTE, _WARNING, _ERROR, _CRITICAL


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
_HTML_LINK = "navigator-link"

_LINK_SEARCH_PREFIX = ">"
_LINK_SEARCH_SUFFIX = "<"


## ========================================================================== ##
##                                    HTML                                    ##
## ========================================================================== ##
class StructToHtml():

    def __init__(self, data:dict, config:dict, root_path:str, suffix:str=".html"):
        self.root_path = root_path
        self.data = data
        self._default_syntax_highlight = config.default.syntaxHighlight
        self._config_data_path = config.display.pathData
        
        self.suffix = suffix

        self.log = []
        self._html_page = ""
        self.done = False
        self.valid = None

    @property
    def html_page(self):
        if not self.done:
            self.generate_html_page()
        return self._html_page


    ## =============================== report =============================== ##
    def log_branch_report(self, importance:int, branch:list, message:str, 
        ) -> None:
        self.log = log_branch_report(log=self.log, importance=importance, 
            branch=branch, message=message, message_limit=240,
            )

    def log_report(self, importance:int, message:str) -> None:
        self.log = log_report(log=self.log, importance=importance, 
                message=message, message_limit=240,
            )

    def print_log(self, min_importance) -> None:
        if not self.done:
            self._run_check()
        print_log(log=self.log, min_importance=min_importance)

    ## ========================= generate_html_page ========================= ##
    def generate_html_page(self) -> None:
        """ Generate HTML document from header and sections.
        """
        # header checkpoint
        valid_header = self.check_html_header(
                header=self.data.get('header', None), 
                importance=_CRITICAL,
            )
        if not valid_header: 
            self.done = True
            self.valid = False
            return
        
        # header html
        html_header = self.create_html_header(
                header=self.data.get('header', None), 
                css_class_list=[],
            )
        
        # sections
        sections = self.data.get('sections', [])
        html_sections = ""
        for section in sections:
            html_section = self.create_html_section(section=section)
            html_sections += html_section

        html_page = \
        f'<div class="{_HTML_PAGE}">\n' \
            f'<script type="application/json" id="page-data">\n' \
                f'{"{"}"pageTitle": "{self.data["header"]["title"]}"{"}"}\n'\
            f'</script>\n'\
            f'<div class="{_HTML_PAGE_HEADER}">'\
                f'{html_header}'\
            f'</div>'\
            f'<div class="{_HTML_PAGE_CONTENT}">\n' \
                f'{html_sections}' \
            f'</div>\n' \
        f'</div>\n'

        self._html_page = html_page
        self.done = True
        self.valid = True
        return


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
            'matchIndex' from data structure. 

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
        link_file = Path(link_file).with_suffix('').with_suffix(self.suffix)
        # link_file = link_file + self.suffix
        link = f"<a "
        if section_tag is not None:
            link += f"section-tag='{section_tag}' "
        link += f"onclick=\"handleClick('{match_string}', '{link_file}')\" "\
                f"onmouseover=\"debouncedHandleHover('{link_file}')\" "
        if css_class is not None:
            link += f"class=\"{_HTML_LINK} {css_class}\""
        else:
            link += f"class=\"{_HTML_LINK}\""
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


    ## ========================= check_html_header ========================== ##
    def check_html_header(
            self, 
            header:dict,
            importance:int,
        ) -> bool:
        valid_header = True
        if header is None:
            self.log_report(
                importance=importance,
                message=f"`header` is missing."
            )
            if importance > _WARNING:
                valid_header = False
        else:
            title = header.get('title', None)
            if title is None:
                self.log_report(
                    importance=importance,
                    message=f"`header.title` is missing."
                )
                if importance > _WARNING:
                    valid_header = False
        return valid_header
        

    ## ========================= create_html_header ========================= ##
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
        if header is None:
            header_html = ""
        else:
            header_html = ""
            css_classes = ' '.join(css_class_list)
            if len(css_classes) > 0:
                css_classes = ' '+css_classes
            title_prefix = header.get('titlePrefix', None)
            if title_prefix is not None:
                header_html += \
                    f'<span class="{_HTML_HEADER_TITLEPREFIX}{css_classes}">'\
                    f'{title_prefix}</span>'
            title = header.get('title', None)
            if title is not None:
                header_html += \
                f'<span class="{_HTML_HEADER_TITLE}{css_classes}">{title}</span>'
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
        # TODO: highlight without numbers, add custom numbers 
        # (to stretch when the code is wrapped)

        if not check_valid_syntax_highlight(syntax_highlight=syntax_highlight):
            syntax_highlight = self._default_syntax_highlight
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
        section_header = section.get('header', dict())
        section_header_html = self.create_html_header(
                header=section_header, 
                css_class_list=[],
            )

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
            include_line_numbers = \
                not (syntax_highlight==self._default_syntax_highlight)

            # section content
            line_number_start = section_content.get('lineNumberStart', None)
            if line_number_start is None:
                line_number_start = get_line_number_from_permalink(
                        permalink=section_header.get('permalink', None),
                    )
            
            
            section_text = section_content.get('text', None)
            section_highlighted_content = \
                self.create_html_section_content(
                    section_text=section_text, 
                    syntax_highlight=syntax_highlight,
                    include_line_numbers=include_line_numbers,
                    line_number_start=line_number_start,
                )

            # links
            links = section.get('links', [])
            if isinstance(links, type(None)): 
                # this may happe if links are `links:` without any content
                links = []
            valid_links_mask = self.check_links(
                links=links,
                section_index=section_index,
            )
            
            for valid_link, (link_index, link) in \
                zip(valid_links_mask, enumerate(links)):
                if not valid_link:
                    self.log_report(
                        importance=_WARNING,
                        message=\
                            f"Skipping `data.sections[{section_index}]."\
                            f"links[{link_index}]' due to previous errors."\
                        )
            
                html_link = \
                    self.create_link(
                            match_string=link['matchString'], 
                            link_file=link['linkFile'],
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
                    self.log_report(
                        importance=_ERROR, 
                        message= \
                        f"No match found for '{link['matchString']}'"\
                        f" from data.sections[{section_index}]."\
                        f"link[{link_index}] in section `text`.")
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
    

    def check_links(self,
                   links:dict,
                   section_index:int,
                ) -> List[bool]:

        # links are optional
        valid_links_mask = []
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
                        dupklicated_indices = \
                            matchStrings.index(link['matchString'])
                        self.log_report(
                            importance=_ERROR,
                            message=\
                                f"Duplicate value for "\
                                f"`data.sections[{section_index}]."\
                                f"links[{link_index}].matchIndex = "\
                                f"{link['matchIndex']}`, with previously "\
                                f"checked links[{dupklicated_indices}]."
                            
                            )
                        # link is duplicate, invalidate link
                        valid_link = False
                valid_links_mask.append(valid_link)
                
        return valid_links_mask        
        
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

    def check_section_link_linkfile(
                self, 
                link:dict, 
                section_index:int, 
                link_index:int,
            ) -> bool:
        valid_linkfile = True
        if 'linkFile' not in link.keys():
            self.log_report(
                importance=_CRITICAL,
                message=\
                    f"Missing member `data.sections[{section_index}]."\
                    f"links[{link_index}].linkFile` but "\
                    f"`linkFile` is compulsory!",
                )            
            valid_linkfile = False
        elif link['linkFile'] == None:
            self.log_report(
                importance=_CRITICAL,
                message=\
                    f"Missing value for `data.sections[{section_index}]."\
                    f"links[{link_index}].linkFile = ''`, but "\
                    f"`linkFile` is compulsory!",
                )
            valid_linkfile = False
        else:
            try:
                if not Path(self.root_path).joinpath(\
                    self._config_data_path, link['linkFile']\
                    ).exists():
                    path_str = str(Path(self.root_path).joinpath(\
                        self._config_data_path, link['linkFile']))
                    self.log_report(
                        importance=_WARNING,
                        message=\
                            f"File path `data.sections[{section_index}]."\
                            f"links[{link_index}].linkFile = '{path_str}'` "\
                            f"is not valid, assure the file exists to avoid "\
                            f"runtime errors (config.display.pathData = "\
                            f"'{self._config_data_path}')!",
                        )
                    
            except Exception as e:
                self.log_report(
                    importance=_ERROR,
                    message=\
                        f"Error checking path for "\
                        f"`data.sections[{section_index}]."\
                        f"links[{link_index}].linkFile`: {str(e)}",
                    )
        return valid_linkfile
    
    
    def check_section_link_matchstring(
                self, 
                link:dict, 
                section_index:int, 
                link_index:int,
            ) -> bool:
        valid_link = True
        if 'matchString' not in link.keys():
            self.log_report(
                importance=_CRITICAL,
                message=\
                    f"Missing member `data.sections[{section_index}]."\
                    f"links[{link_index}].matchString` but "\
                    f"`matchString` is compulsory!",
                )
            valid_link = False
        elif link['matchString'] == None:
            self.log_report(
                importance=_CRITICAL,
                message=\
                    f"Missing value for `data.sections[{section_index}]."\
                    f"links[{link_index}].matchString = ''`, "\
                    f"matchString cannot be empty, valid values: "\
                    f"1) empty [], "\
                    f"2) only positive including `0` [0, 2], "\
                    f"3) only negative [-2 -5]",
                )
            valid_link = False
        return valid_link