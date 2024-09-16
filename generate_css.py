from pygments.formatters import HtmlFormatter

import argparse
import sys
from pathlib import Path

import os
import yaml

## ========================================================================== ##
##                                    UTILS                                   ##
## ========================================================================== ##
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


    directory = Path(args.directory)
    if not directory.exists():
        print(f"Error: The specified relative directory does not exist: {directory}")
        sys.exit(1)

    style = args.style
    if style == "None":
        style = config['default']['pygmentsStyle']
    

    # console output
    print_headline(headline='Generating CSS files', fill='-', width=80)
    print(f"Target directory: {directory}")
    # You can now continue with your own code using these variables
    css, css_default = get_pygments_css(
            style=style, 
            default_style=config['default']['pygmentsStyle'],
        )

    full_css_path = Path(directory, 'pygments_style.css')
    with open(full_css_path, "w") as file:
        file.write(css)

    full_css_path = Path(directory, 'pygments_style_default.css')
    with open(full_css_path, "w") as file:
        file.write(css_default)


    print_headline(
            headline=f'Generated CSS)',
            fill='#', 
            width=80,
        )
    
    
if __name__ == "__main__":
    main()



