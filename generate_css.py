from pygments.formatters import HtmlFormatter

import argparse
import sys
from pathlib import Path

import os
import yaml

from types import SimpleNamespace
import json
from python_lib.log import print_headline, print_notice, print_report, \
    log_reset_prepend, _NOTE, _CRITICAL


## ========================================================================== ##
##                                    CSS                                     ##
## ========================================================================== ##
def get_pygments_css(style:str, default_style:str):
    """ Return a 2 CSS files, one for the theme requested by the user, 
    the second as a default 

    :param style: Name of a style recognized by 
    :param config: _description_
    :raises ValueError: _description_
    :raises ValueError: _description_
    :return: _description_
    """
    try:
        formatter = HtmlFormatter(style=style)
    except:
        raise ValueError(f"HtmlFormatter does not recognize style='{style}'!")
    css = formatter.get_style_defs()

    try:
        default_formatter = HtmlFormatter(style=default_style)
    except:
        raise ValueError(f"HtmlFormatter does not recognize style='{style}'!")
    css_default = default_formatter.get_style_defs()

    return css, css_default


## ========================================================================== ##
##                                    main                                    ##
## ========================================================================== ##
def main():
    
    # reset global variable
    log_reset_prepend()
    
    # Command Line Interface
    parser = argparse.ArgumentParser(
        description=\
            f"Generate pygments_style.css and pygments_style_default.css "\
            f"file into ./css directory.")
    parser.add_argument("-d", "--directory", 
            default=str(Path(__file__).parent.joinpath('css')),
            help=f"Path to directory where the script will "\
                f"execute (default: script's directory)")
    parser.add_argument("-s", "--style", 
            default='None',
            help=f"Pygmentize style, see https://dt.iki.fi/pygments-gallery")
    parser.add_argument("-c", "--config", 
            default=str(Path(__file__).parent.joinpath("config.yaml")),
            help=f"Path to config file "\
                f"(default: config.yaml in script's directory)")
    args = parser.parse_args()

    # get config
    if os.path.isabs(args.config):
        config = Path(args.config)
    else:
        config = Path(Path(__file__).parent.joinpath(args.config))
        
    # process config argument
    if os.path.isabs(args.config):
        config_path = Path(args.config)
    else:
        config_path = Path(Path(__file__).joinpath(args.config))
    if not config_path.exists():
        print_report(
            importance=_CRITICAL, 
            message=f"The specified config file does not exist: "\
                    f"{config_path}")
        sys.exit(1)
    else:
        try:
            def load_object(dct):
                return SimpleNamespace(**dct)
            with open(config_path, 'r') as file:
                config_dict = yaml.safe_load(file)
                config = json.loads(json.dumps(config_dict), 
                                    object_hook=load_object)
                config.dataStructure = config_dict['dataStructure']
        except Exception as e:
            print_report(
                importance=_CRITICAL, 
                message=f"The specified config file cannot be parsed: {e}")
            sys.exit(1)

    # check directory
    directory = Path(args.directory)
    if not directory.exists():
        print_report(
            importance=_CRITICAL, 
            message=f"invalid path: {str(directory)}")
        print_notice(notice="FAILED", fill='!')
        sys.exit(1)

    # check style
    style = args.style
    if style == "None":
        style = config.default.pygmentsStyle
    
    # console output
    print_headline(headline='Generating CSS files', fill='-', width=80)
    
    # generate files
    css, css_default = get_pygments_css(
            style=style, 
            default_style=config.default.pygmentsStyle,
        )
    
    # save files
    full_css_path = Path(directory, 'pygments_style.css')
    with open(full_css_path, "w") as file:
        file.write(css)
    print_report(
        importance=_NOTE, 
        message=f"generating '{str(full_css_path)}'")
    full_css_path = Path(directory, 'pygments_style_default.css')
    with open(full_css_path, "w") as file:
        file.write(css_default)
    print_report(
        importance=_NOTE, 
        message=f"generating '{str(full_css_path)}'")
    
    # print to console
    print_notice(notice="SUCCESS", fill='~')
    
    
if __name__ == "__main__":
    main()



