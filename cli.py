"""Command-line Interface for interaction with the tool
"""

# Modules
## Internal
## External
import sys, json
import datetime
import os
import hashlib


# Parameters

# Methods
## JSONs
def jload( fp ):
    with open( fp, 'r' ) as in_file:
        result = json.load( in_file )
    return( result )
def jdump( obj, fp ):
    with open( fp, 'w' ) as out_file:
        json.dump( obj, out_file, ensure_ascii = False, sort_keys = True )
    return
## DatetimeStr
def datetime_to_str( _datetime ):
    return(str(_datetime)[:19].replace('-','').replace(' ','').replace(':',''))
## SHA1
def sha1(s):
    return hashlib.sha1(bytes(s,'utf-8')).hexdigest()



# Classes
class CLI:
    """Command-line Interface to interact with
    
    Parameters:
    - path_configs
    - path_data
    
    TODO:
    - add following commands: 'add', 'list', 'search', 'remove'
    - add @2 and @4 as aliases for "to" and "from" a person
    """
    # Constructor
    def __init__( self, path_configs ):
        # Parameters
        self.path_configs = path_configs
        self.configs = jload( self.path_configs )
        ## Specific Parameters
        self.path_data = self.configs['path_data']
        # Implemented Commands
        self.commands_implemented = {
            'add': self.add,
            # 'list': self.list,
            # 'search': self.search,
            # 'remove': self.remove,
        }
        # Return
        return
    # Execute
    def execute( self, argv ):
        # Extract
        command, arguments = argv[1], argv[2:]
        command = command.lower()
        # Execute
        successful, message = self.commands_implemented[command](arguments)
        # Report
        print( '{:<10} : {}'.format(
            'SUCCESSFUL' if successful else 'FAILED',
            message
        ) )
        # Return
        return( successful )
    # Add
    def add( self, arguments ):
        # Text
        text = ' '.join(arguments)
        text_sha1 = sha1( text )
        # Get Datetime
        datetime_now = datetime.datetime.now()
        datetime_str = datetime_to_str(datetime_now)
        # File Path
        file_name = '{}_{}.json'.format(
            datetime_str,
            text_sha1[:16]
        )
        fp_write = os.path.join(
            self.path_data,
            file_name
        )
        # Result
        result = {
            "datetime": str(datetime_now),
            "text_sha1": text_sha1,
            "text": text
        }
        # Store
        try:
            jdump( result, fp_write )
        except Exception as e:
            return( False, str(e) )
        # Successful
        return( True, 'note stored at "{}"'.format( fp_write ) )
        



# Main
if __name__ == '__main__':
    # ArgV
    argv = sys.argv
    # Create CLI
    cli = CLI( 'configs.json' )
    # Report
    print( len(argv) )
    for i, v in enumerate( argv ):
        print( "Arg {:>2} : '{}'".format( i, v ) )
    print('-#'*20)
    # Report
    if( len(argv) >= 3 ):
        successful = cli.execute( argv )
    
    
































