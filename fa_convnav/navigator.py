# AUTOGENERATED! DO NOT EDIT! File to edit: 01_navigator.ipynb (unless otherwise specified).

__all__ = ['convnav_supported_models', 'cndf_view', 'add_container_row_info', 'cndf_search', 'ConvNav', 'cndf_save',
           'cndf_load']

# Cell
import pickle
from .models import models
from .core import *
from pandas import DataFrame, option_context, concat
from math import ceil

# Cell
def convnav_supported_models():
  "Prints list of transfer learning models supported by fa_convnav"
  supported_models()

# Cell
def cndf_view(df, verbose=3, truncate=0, tight=True, align_cols='left', top=False):
    "Display a valid CNDF dataframe `df` with optional arguments and styling"

    def check_view_args(df, verbose, truncate):
      assert type(df) == DataFrame and 'Module_name' in df.columns, "Not a valid convnav dataframe"
      assert isinstance(truncate, int) and -10 <= truncate <= 10, f"Argument 'truncate' must be an integer between -10 (show more cols) and +10 (show fewer cols)"
      assert isinstance(verbose, int) and 1 <= verbose <= 5, f"Argument verbose must be 1 2 or 3 "

    def display_df(df, verbose, truncate, tight, align_cols):
      with option_context("display.max_rows", 1000):
        df.index.name = 'Index'
        df_styled = df.iloc[:,:-(11+truncate)].style.set_properties(**{'text-align': align_cols})
        if tight:
          display(df_styled)
        else:
          display(df.iloc[:,:-(11+truncate)])

    #handle arguments
    check_view_args(df, verbose, truncate)
    if not isinstance(tight, bool): tight = True
    if len(df) < 10: tight = False
    if verbose != 3: truncate = (10, 4, 0, 0, -10)[verbose-1]
    if verbose == 4: df = add_container_row_info(df)

    #display df
    if top and len(df) > 10:
      display_df(df.iloc[:10], verbose, truncate, False, align_cols)
      print(f'...{len(df)-10} more layers')
    elif len(df) > 0:
      display_df(df, verbose, truncate, tight, align_cols)
    else:
      print('No data to display')
    return None

# Cell
def add_container_row_info(df):
    "Add output dimensions and block/layer counts to container rows of `df`. These are not added when a CNDF dataframe is first built to avoid cluttering the display of larger dataframes."
    df.loc[df['Division'] == '', 'Division'] = df['div_id']
    df.loc[df['Container_child'] == '', 'Container_child'] = df['chd_id']
    df.loc[df['Container_block'] == '', 'Container_block'] = df['blk_id']
    df.loc[df['Output_dimensions'] == '', 'Output_dimensions'] = df['out_dim']
    df.loc[df['Currently'] == '', 'Currently'] = df['current']
    return df

# Cell
def cndf_search(df, searchterm, exact=True, show=True):
  "Search a CNDF dataframe, display the results in a dataframe and return matching module object(s)"

  def match(df, searchterm, exact):
    "Searches `df` for `searchterm`, returning exact matches only if `exact=True` otherwise any match"

    #select 'df' row using index from 'searchterm'
    if isinstance(searchterm, int):
      assert searchterm >= 0 and searchterm <= len(df), f'Layer ID out of range: min 0, max {len(df)}'
      x = df.iloc[searchterm].copy()
      x = DataFrame(x).transpose()
      return x

    #if searchterm is a float assume it is a layer name (i.e. format 0.0.1) and convert to string
    if isinstance(searchterm, float): searchterm = str(searchterm)

    #select rows matching the conditional df[key] ==/contains value (exact=True/false) for dict
    if isinstance(searchterm, dict):

      for col, s in searchterm.items():
        assert col in df.columns, f'{col} not a valid column identifier. Valid column names are {df.columns}'
        return df[df[col] == s].copy() if exact else df[df[col].str.contains(s)].copy()
      return x

    #select rows in df where df[col] ==/contains searchterm string (exact=True/False)
    if isinstance(searchterm, str):
      searchterm = searchterm.strip(' \.')
      cols = {'Module_name', 'Torch_class', 'Division', 'Container_child', 'Container_block', 'Layer_description'}
      if exact:
        for col in cols:
          x = df[df[col] == searchterm].copy()
          if not x.empty: return x
      else:
        for col in cols:
          x = df[df[col].str.contains(searchterm)].copy()
          if not x.empty: return x
      return x

    assert True, 'Unrecognizable searchterm'

  def process_searchterm(df, searchterm, exact):
    "Search 'df` for single or combination of modules and layers. If df = None, searches instance dataframe `self._cndf` (default)"

    #if searchterm is a `float` assume it is a layer name (i.e. format 0.0.1) and convert to `string`
    if isinstance(searchterm, float): searchterm = str(searchterm)

    if isinstance(searchterm, int):
      return match(df, searchterm, True)
    elif isinstance(searchterm, str):
      return match(df, searchterm, exact)
    #concatenate successive search results (logical 'OR') for series of dicts
    elif isinstance(searchterm, dict):
      _df = DataFrame()
      for col, s in searchterm.items():
        new_df = match(df, {col:s}, exact)
        _df = concat((_df, new_df), axis=0, ignore_index=False).drop_duplicates('Module_name')
      return _df
    #concatenate successive search results (logical 'OR') in list
    elif isinstance(searchterm, list):
      _df = DataFrame()
      for s in searchterm:
        new_df = match(df, s, exact)
        _df = concat((_df, new_df), axis=0, ignore_index=False).drop_duplicates('Module_name')
      return _df
    #recursively call match on _df to logical 'AND' successive search results in tuple
    elif isinstance(searchterm, tuple):
      _df = df.copy()
      for s in searchterm:
        _df = match(_df, s, exact)
      return _df
    else:
      assert True, 'Unrecognizable searchterm'

  #get search results
  df_res = process_searchterm(df, searchterm, exact)

  #show matches and return corresponding modules
  if df_res is not None and not df_res.empty:
    if show:
      print(f'{len(df_res)} layers found matching searchterm(s): {searchterm}\n')
      cndf_view(df=df_res)
    return df_res['lyr_obj'].tolist()
  else:
    if show: print(f'No matches for searchterm(s): {searchterm}\n')
    return None

# Cell
class ConvNav(CNDF):
  "Builds a CNDF dataframe representation of a CNN model from a fastai `Learner` object and `Learner.summary()`. \
  Provides methods to view, search and select model layers and modules for further investigation."

  def __init__(self, learner, learner_summary):
    super().__init__(learner, learner_summary)

  def __len__(self):
    return len(self._cndf)

  def __str__(self) -> str:
    return self.model_info

  def __call__(self):
    self.view(top=True)

  def __contains__(self, s):
    return self.search(s)

  def search(self, searchterm, **kwargs):
    "Find `searchterm` in instance dataframe, display the results and return matching module object(s). See `cndf_search()` for kwargs."
    return cndf_search(self._cndf, searchterm, **kwargs)

  def view(self, **kwargs):
    "Display instance CNDF dataframe with optional arguments and styling (see `cndf_view()` for kwargs)"
    print(f'{self.model_info}\n')
    cndf_view(self._cndf, **kwargs)

  def _view(self, df, add_info=False, **kwargs):
    "Add output dimensions and block/layer counts to Container rows of `df` then display `df`"
    _df = df.copy()
    if add_info:
      _df = add_container_row_info(_df)
    cndf_view(_df, **kwargs)

  @property
  def head(self):
    "View module of model head"
    df = self._cndf.copy()
    df = df[df['Module_name'].str.startswith('1')]
    if not df.empty:
      res = f"{self.model_type.capitalize()}: {self.model_name.capitalize()}\n"
      res += f"Input shape: {self._cndf.iloc[1]['out_dim']} (bs, filt, h, w)\n"
      res += f"Output features: {self.output_dimensions} (bs, classes)\n"
      print(res)
      self._view(df, truncate=1)
    else:
      res = "Model has no head"
      print(res)


  @property
  def body(self):
    "View modules of model body"
    df = self._cndf.copy()
    df = df.loc[df['Module_name'].str.startswith('0')]
    if not df.empty:
      res = f"{self.model_type.capitalize()}: {self.model_name.capitalize()}\n"
      res += f"Input shape: {self.input_sizes} (bs, ch, h, w)\n"
      res += f"Output dimensions: {df.iloc[-1]['Output_dimensions']} (bs, filt, h, w)\n"
      res += f"Currently frozen to parameter group {self.frozen_to} out of {self.num_param_groups}\n"
      print(res)
      self._view(df)
    else:
      res = "Model body has no contents"
      print(res)


  @property
  def divs(self):
    "Summary info for model head and body"
    df = self._cndf.copy()
    df = df.loc[(df['Module_name'] == '0') | (df['Module_name'] == '1')]

    for i in range(2):
      df_div = self._cndf.loc[self._cndf['div_id'] == str(i)].copy()
      df.iloc[i]['Model'] = self.model_name
      df.iloc[i]['Container_child'] = len(df_div[df_div['Container_child'] != ''])
      df.iloc[i]['Container_block'] = len(df_div[df_div['Container_block'] != ''])
      df.iloc[i]['Layer_description'] = len(df_div[df_div['Layer_description'] != ''])
      params = df_div['Parameters'].values
      params_int = [int(x.replace(',','')) for x in params if x != '']
      params_summed = sum(params_int)
      df.iloc[i]['Parameters'] = params_summed

    df['Output_dimensions'] = df['out_dim']
    df.iloc[0]['Currently'] = df.iloc[0]['current']

    df = df.rename(columns={'Container_child': 'Container_child (num)', 'Container_block': 'Container_block (num)', 'Layer_description': 'Layers'})
    res = f"{self.model_type.capitalize()}: {self.model_name.capitalize()}\n"
    res += f"Input shape: [{self.inp_sz}] (bs, ch, h, w)\n"
    res += f"Divisions:  body (0), head (1)\n"
    print(res)
    self._view(df)


  @property
  def dim_transitions(self):
    "Finds layers with different input and output dimensions. These are useful points to apply hooks and callbacks for investigating model activity."
    df = self._cndf.copy()
    df = df[df['Torch_class'].str.contains('Conv2d')]

    n = []
    old_dims = 0
    for i, row in enumerate(df.iterrows()):
      row=row[1]
      new_dims = row['Output_dimensions'].rstrip(']').split(' x ')[-1]
      if new_dims != old_dims:
        n.append(i)
        old_dims = new_dims
    df = df.iloc[n]

    print(f"{self.model_name.capitalize()}\nLayer dimension changes\n")
    self._view(df, add_info=True)
    return df['lyr_obj'].tolist()


  @property
  def linear_layers(self):
    "Displays and returns all linear layers in the `model`"
    df = self._cndf.copy()
    df = df[df['Torch_class'].str.contains('Linear')]
    df['Division'] = df['div_id']

    print(f"{self.model_name.capitalize()} linear layers\n")
    self._view(df, truncate=1, tight=False)
    return df['lyr_obj'].tolist()


  def frozen_vs_unfrozen(self, col, req):
    "Displays and returns all frozen vs unfrozen modules and layers"
    df = self._cndf.copy()
    df = df.loc[df['div_id'] == '0']
    col = col.lower()
    req_substr = req[req.find(' ')+1:].capitalize()

    if col == 'layer':
      df = df[df['Currently'] == req_substr]
    elif col == 'block':
      df = df.loc[(df['Container_block'] != '') & (df['current'] == req_substr)]
    else:
      df = df.loc[(df['Container_child'] != '') & (df['current'] == req_substr)]

    if req == 'Last frozen': df=df.iloc[-1:, :]
    if req == 'First unfrozen': df=df.iloc[:1, :]

    print(f"{self.model_name}\n{req} {col}(s): ")
    self._view(df, add_info=True)
    return df['lyr_obj'].tolist()

  def frozen(self, col='child'):
    "Displays and returns all frozen child container (`col='child'`), block container (`col='block'`) or layers (`col='layer'`)."
    return self.frozen_vs_unfrozen(col, 'All frozen')

  def unfrozen(self, col='child'):
    "Displays and returns all unfrozen child container (`col='child'`), block container (`col='block'`) or layers (`col='layer'`)."
    return self.frozen_vs_unfrozen(col, 'All unfrozen')

  def last_frozen(self, col='child'):
    "Displays and returns the last frozen child container (`col='child'`), block container (`col='block'`) or layer (`col='layer'`)."
    return self.frozen_vs_unfrozen(col, 'Last frozen')

  def first_unfrozen(self, col='child'):
    "Displays and returns the first unfrozen child container (`col='child'`), block container (`col='block'`) or layer (`col='layer'`)."
    return self.frozen_vs_unfrozen(col, 'First unfrozen')


  def structs(self, col):
    "Display container elements of model body"
    df = self._cndf.copy()
    df = df.loc[df['div_id'] == '0']
    df = df[df[col] != '']

    df = add_container_row_info(df)

    if col == 'Container_block':
      df['Layer_description'] = df['lyr_blk']
      df.rename(columns={'Layer_description': 'Num_layers'}, inplace=True)

    if col == 'Container_child':
      df['Container_block'] = df['blk_chd']
      df.rename(columns={'Container_block': 'Num_blocks'}, inplace=True)
      df.loc[df['Layer_description'] == '', 'Layer_description'] = df['lyr_chd']
      df.rename(columns={'Layer_description': 'Layer_description (or num layers if > 1)'}, inplace=True)

    print(f"{self.model_name}\n{'Blocks' if col == 'Container_block' else 'Children'} ")
    self._view(df, tight=False)
    return df['lyr_obj'].tolist()

  @property
  def children(self):
    "Display and return child container modules (equivelent to fastai `Learner.model.children()`)"
    return self.structs('Container_child')

  @property
  def blocks(self):
    "Display and return block container modules"
    return self.structs('Container_block')


  def find_conv(self, req='all', num=1, in_main=False):
    "Finds the first (`req=First`) or last (`req=last`) `num` Conv2d layers in the model body. Set `in_main=True` to return conv layers from the main body of the model only."

    valid_reqs = ['all', 'first', 'last']
    assert req.lower() in valid_reqs, f'Invalid request: req must be one of {valid_reqs}'

    df = self._cndf.copy()
    df = df[df['tch_cls'] == 'Conv2d']
    assert isinstance(num, int) and num > 0, f'Number must be a positive integer'
    if num >= len(df): num = len(df)-1

    if in_main:
      df = df.iloc[1:]

    if req == 'first':
      df = df.iloc[:num,:]
    elif req == 'last':
      df = df.iloc[num*-1:,:]
    else: pass

    print(f"{self.model_name}\n{req.capitalize()} {'' if req=='all' else num} Conv2d layers\n")
    self._view(df, tight=False)
    return df['lyr_obj'].tolist()


  def find_block(self, b, layers=True, layers_only=False):
    "Finds, displays and returns container blocks by module name `b`"

    #strip preceeding '0.'s from module name so search starts from same point in all models
    while b.startswith('0') or b.startswith('.'):
      b = str(b).strip('0\.')
    b = b.split('.')
    assert len(b) == 2, "Module name does not specify a block element: try something like '6.1' or '0.6.1'"

    df = self._cndf.copy()
    df = df[(df['chd_id'] == b[0]) & (df['blk_id'] == b[1])]

    if not layers:
      df = df[df['Layer_description'] == '']
      df['Layer'] = df['lyr_blk']
      df.rename(columns={'Layer_description': 'Num_layers'}, inplace=True)
      layers_only = False

    if layers_only:
      df = df[df['Layer_description'] != '']

    print(f"{self.model_name}\nBlock 0.{b[0]}.{b[1]}\n")
    self._view(df, add_info=True)
    return df['lyr_obj'].tolist()


  def spread(self, req='conv', num=5):
    "Returns `num` of equally spaced `req` elements over the model. `req` = 'conv', 'block', or 'child'"

    valid_reqs = ['Child', 'Block', 'Layer', 'Conv2d', 'Conv2D', 'Conv']
    req = req.capitalize()
    assert req in valid_reqs, f'Invalid request: req must be one of {valid_reqs}'
    assert isinstance(num, int), 'Number must be an integer'
    num = max(3, num)

    df = self._cndf.copy()
    df = df[df['div_id'] == '0'][1:]

    if 'Child' in req:
      df = df[df['Container_child'] == 'Sequential']
    elif req == 'Block':
      df = df[df['Container_block'] != '']
    else:
      df = df[df['tch_cls'] == 'Conv2d']

    num = min(len(df), num)

    df = add_container_row_info(df)

    if len(df) > num:
      n = list(range(0, len(df), (ceil(len(df)/num))))
      n.pop()
      n.append(len(df)-1)
      df = df.iloc[n]

    if  req == 'Child' or req == 'Block':
      df['Layer_description'] = df['lyr_blk']
      df.rename(columns={'Layer_description': 'Num_layers'}, inplace=True)

    if req == 'Child':
      df['Container_block'] = df['blk_chd']
      df.rename(columns={'Container_block': 'Num_blocks'}, inplace=True)
      df['Num_layers'] = df['lyr_mod']

    print(f"{self.model_name}\nSpread of {req.lower()} where n = {num}\n")
    self._view(df)
    return df['lyr_obj'].tolist()


# Cell
def cndf_save(cn, filename, path='', with_modules=False):
  "Saves the instance dataframe `cn._cndf` to persistent storage at `path` with `filename` gzip compresseed"
  df = cn._cndf.copy()
  if not with_modules: df = df.iloc[:,:-1]
  with gzip.open(path+filename, "wb") as f:
    pickle.dump(df, f, pickle.HIGHEST_PROTOCOL)

# Cell
def cndf_load(filename, path=''):
  "Loads a CNDF dataframe from persistent storage at `path`+`filename` and unzips it."
  with gzip.open(path+filename, "rb") as f:
    return pickle.load(f)