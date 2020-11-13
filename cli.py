"""Command-line Interface for interaction with the tool
"""

# Modules
## Internal
## External
import datetime
import hashlib
import json
import os
import re
import sys


# Parameters

# Methods
## JSONs
def jload( fp ):
    with open( fp, 'r' ) as in_file:
        result = json.load( in_file )
    return( result )
def jdump( obj, fp ):
    with open( fp, 'w' ) as out_file:
        json.dump( obj, out_file, ensure_ascii = False, sort_keys = True, indent = 1 )
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
    - add 'indexer' to index contentp
        - list of people
        - list of hashtags
        - list of words?
        - date, time, datetime, "yesterday", "last_week", ...
    - add following commands: 'search', 'remove'
    - add @2 and @4 as aliases for "to" and "from" a person
    """
    # Constructor
    def __init__( self, path_configs ):
        # Parameters
        self.path_configs = path_configs
        self.configs = jload( self.path_configs )
        ## Specific Parameters
        self.path_data = self.configs['path_data']
        self.max_list_results = self.configs['max_list_results']
        # Load/Create Indices
        self.load_or_create_indices()
        # Implemented Commands
        self.commands_implemented = {
            'add': self.add,
            'list': self.list,
            'index': self.index,
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
        print( '{:<10} <{}> : {}'.format(
            'SUCCESSFUL' if successful else 'FAILED',
            command.upper(),
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
    # List Files
    def _list_files( self ):
        # List
        try:
            self.file_names = [
                x for x in sorted( os.listdir( self.path_data ) )[::-1] if x.endswith('.json') and len(x) == 36
            ]
            self.file_paths = [
                os.path.join( self.path_data, fn ) for fn in self.file_names
            ]
            self._trace = '<trace> Successful'
        except Exception as e:
            self.file_names = None
            self.file_paths = None
            self._trace = '<trace> ' + str(e)
        # Return
        return
    # List
    def list( self, arguments ):
        # Get Datetime
        datetime_now = datetime.datetime.now()
        datetime_str = datetime_to_str(datetime_now)
        # List
        self._list_files()
        if( self.file_names is None ):
            return( False, self._trace )
        # Report
        print( 'Total notes found: {:>9}'.format( len(self.file_names) ) )
        if( len(self.file_names) > 0 ):
            print('\n{:<14} | {:<16} | {} | {}'.format( 'Note Taken At', 'Text Identifier', 'Note Path', 'Text Head' ))
            print('-'*( 14+3+16+3+len(self.path_data)+1+36+3+75 ))
        for fn, fp in zip( self.file_names[:self.max_list_results], self.file_paths ):
            _datetime, _sha1 = fn[:-5].split('_')
            head = jload(fp)['text'][:75].replace('\n', ' ')
            print('{} | {} | {} | {}'.format( _datetime, _sha1, fp, head ))
        if( len(self.file_names) > self.max_list_results ):
            print('...')
        if( len(self.file_names) > 0 ):
            print('-'*( 14+3+16+3+len(self.path_data)+1+36+3+75 ))
        # Successful
        return( True, 'notes at "{}" listed'.format( self.path_data ) )
    # Load Indices
    def load_or_create_indices( self ):
        # Path
        fp_read = os.path.join(
            self.configs['path_data'],
            '_indices'
        )
        # Load/Create
        if( os.path.exists( fp_read ) ):
            self.indices = jload( fp_read )
        else:
            self.indices = {
                'token_map': dict()
            }
        ## Token Map
        self.token_map = self.indices['token_map']
        # Return
        return
    # Store Indices
    def store_indices( self ):
        # Path
        fp_write = os.path.join(
            self.configs['path_data'],
            '_indices'
        )
        # Store
        jdump( self.indices, fp_write )
        # Return
        return
    # Index
    def index( self, arguments ):
        # Regular Expressions: RegExp
        PATTERN_TO_REMOVE = re.compile( '[!\.,\?]' )
        # Get Datetime
        datetime_now = datetime.datetime.now()
        datetime_str = datetime_to_str(datetime_now)
        # List
        self._list_files()
        if( self.file_names is None ):
            return( False, self._trace )
        # Template
        n_files = len(self.file_names)
        msg_prgs_tmpl = '<indexing> Progress: {{:>4}}/{:<4}'.format( n_files )
        # Loop over Files
        for i, (file_name, file_path) in enumerate(zip( self.file_names, self.file_paths )):
            # Report
            print(msg_prgs_tmpl.format(i+1), end = '\r')
            # Already Indexed
            if( file_name in self.indices ):
                continue
            # Index
            ## Load Text
            text_transformed = PATTERN_TO_REMOVE.sub(' ', jload(file_path)['text'])
            ## Tokens
            tokens = set( text_transformed.split() )
            tokens_new = {
                x for x in tokens if not x in self.token_map
            }
            ## Update Token Map
            self.token_map.update(dict(zip(
                tokens_new,
                range( len(self.token_map), len(self.token_map)+len(tokens_new) )
            )))
            ## Indices
            self.indices[file_name]= {
                'tokens': sorted([ self.token_map[x] for x in tokens ])
            }
        print(msg_prgs_tmpl.format(n_files))
        # Store
        try:
            self.store_indices()
        except Exception as e:
            return( False, str(e) )
        # Successful
        return( True, 'notes at "{}" indexed'.format( self.path_data ) )
        
        


# Main
if __name__ == '__main__':
    # ArgV
    argv = sys.argv
    # Create CLI
    cli = CLI( 'configs.json' )
    # Report
    if( len(argv) >= 2 ):
        successful = cli.execute( argv )
    
    
































