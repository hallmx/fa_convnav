# AUTOGENERATED! DO NOT EDIT! File to edit: 01_navigator.ipynb (unless otherwise specified).

__all__ = ['get_row', 'find_model', 'split_infos', 'get_inp_sz', 'infos_to_gen', 'CNDF', 'CNDFView', 'CNDFSearch',
           'ConvNav', 'save_cndf', 'load_cndf']

# Cell
import gzip, pickle, re
from .models import models
from dataclasses import dataclass
from pandas import DataFrame, option_context, read_pickle

# Cell
def get_row(l, m):
  "Construct dataframe row from `l` (Learner.named_modules() layer) and `m` (model)"

  # create generic row data from `l` (model.named_module() layer) and `m` (model_type)
  lyr_name = l[0]
  lyr_obj = l[1]
  ln_split = str(lyr_name).split('.', 4)
  ln_n_splits = len(ln_split)
  lyr_str = str(lyr_obj)

  tch_cls_str = str(type(lyr_obj))
  tch_cls_substr =  tch_cls_str[tch_cls_str.find("<class")+8: tch_cls_str.find(">")-1]
  tch_cls = tch_cls_substr.split('.')[-1]

  div = tch_cls if lyr_name == '0' or lyr_name == '1' else ''
  mod = tch_cls if ln_n_splits == 2 else ''
  blk = tch_cls if ln_n_splits == 3 and not lyr_name.startswith('1') else ''
  lyr = lyr_str[:90]

  # customise generic row for peculiarities of specific models
  if m == 'vgg' or m == 'alexnet':
    if ln_n_splits >2: ln_split[2] = ''
    blk = ''

  elif m == 'squeezenet':
     blk = tch_cls if ln_n_splits == 3 and tch_cls == 'Fire' else ''
     if blk == 'Fire': lyr = ''

  elif m == 'resnet':
    if blk == 'BasicBlock' or blk == 'Bottleneck': lyr = ''
    else:
      if ln_n_splits > 4: lyr = f". . {lyr_str[:86]}"
      if ln_n_splits == 4 and ln_split[3] == 'downsample': lyr = f'Container{tch_cls}'

  elif m == 'densenet':
    lyr_name = lyr_name.replace('denseblock', '').replace('denselayer', '')
    ln_split = str(lyr_name).split('.', 4)
    mod = tch_cls if (lyr_name.startswith('0') and ln_n_splits == 3) or (lyr_name.startswith('1') and ln_n_splits == 2) else ''
    blk = tch_cls if ln_n_splits == 4 and tch_cls == '_DenseLayer' else ''
    if mod == '_DenseBlock' or mod == '_Transition' or blk == '_DenseLayer':
      lyr = ''
    else:
      if lyr_name == '0' or lyr_name == '1': div = tch_cls
      if lyr_name == '0.0': div = f'. {tch_cls}'

  elif m == 'xresnet':
    blk = tch_cls if ln_n_splits == 3 and tch_cls == 'ResBlock' else ''
    if mod == 'ConvLayer' or blk == 'ResBlock':
      lyr = ''
    else:
      if ln_n_splits < 4: lyr =  lyr_str[:90]
      elif ln_n_splits == 4 and tch_cls == 'Sequential': lyr =  f'Container{tch_cls}'
      elif ln_n_splits == 4 and tch_cls == 'ReLU': lyr =  lyr_str[:90]
      elif ln_n_splits == 5 and tch_cls == 'ConvLayer': lyr =  f'. . Container{tch_cls}'
      else: lyr =  f'. . . . {lyr_str[:32]}'

  else:
    raise Exception("Model type not recognised")

  return {
      'Module_name': lyr_name,
      'Model': tch_cls if lyr_name == '' else '',
      'Division': div,
      'Container_child': mod,
      'Container_block': blk,
      'Layer_description': lyr,
      'Torch_class': tch_cls_substr,
      'Output_dimensions': '',
      'Parameters': '',
      'Trainable': '',
      'Currently': '',
      'div_id': ln_split[0] if ln_n_splits >0 else '',
      'chd_id': ln_split[1] if ln_n_splits >1 else '',
      'blk_id': ln_split[2] if ln_n_splits >2 else '',
      'lyr_id': ln_split[3] if ln_n_splits >3 else '',
      'tch_cls': tch_cls,
      'out_dim': '',
      'current': '',
      'lyr_blk': '',
      'lyr_chd': '',
      'blk_chd': '',
      'lyr_obj': lyr_obj
      }

# Cell
def find_model(n):
    "Returns tuple of model type and name (e.g. ('resnet', 'resnet50')) given `n`, the number of named_modules in Learner.model.named_modules()"
    for d in models:
      match = [(k, m) for k, v in d.items() for m, l in v if l == n]
      if match != []: break
    if len(match) > 0: return match[0] # (model_type, model_name)
    assert True, 'Model not supported. Use `supported_models()` to get a list of supported models.'

# Cell
def split_infos(infos):
  "Split the rows of infos (learner.summary()) into separate rows"
  return infos.split('\n')

# Cell
def get_inp_sz(infos):
  "Slice first row of `infos` to give string representation of model input sizes "
  inp_sz = infos[0]
  inp_sz_str = inp_sz[inp_sz.find("['")+2:inp_sz.find("']")]
  return inp_sz_str

# Cell
def infos_to_gen(infos):
  "Slice the remaining rows of `infos` to give the layers, `m`, output dimensions `o`, parameters `p` and trainable `t` of each layer and return (m,o,p,t) for all layers in a generator"
  lyr_info = infos[4:-17][::2]
  info_list = []
  for l in lyr_info:
    m, *s, p, t = [y for y in l.split(' ') if y !=""]
    info_list.append((m, f"[{' '.join(s)}]", p, t))
  return (i for i in info_list)

# Cell
@dataclass
class CNDF:
  "Compile information from fastai `Learner.model` and 'layer_info(Learner)` into a dataframe"
  learner: any
  learner_summary: str

  def __post_init__(self):
    assert hasattr(self.learner, 'model'), "Invalid learner: no 'model' attribute"
    self.model = self.learner.model                                         # fastai `Learner.model` object
    self.layers = list(self.learner.model.named_modules())                  # fastai `named_modules` method
    self.num_layers = len(self.layers)
    self.model_type, self.model_name = find_model(self.num_layers)

    infos_split = split_infos(self.learner_summary)                         # fastai `Learner.summary()` string
    self.inp_sz = get_inp_sz(infos_split)
    self.bs = self.inp_sz[0]
    info_gen = infos_to_gen(infos_split)

    # create base dataframe `df` from a list of formatted rows in `layers`
    df = DataFrame([get_row(l, self.model_type) for l in self.layers])

    # remove layer descriptions from container rows
    df.at[0, 'Layer_description'] = ''
    df.loc[(df['Division'].str.contains('Sequential')) | \
          (df['Container_child'] == 'Sequential') | \
          (df['Container_child'] == 'AdaptiveConcatPool2d'), 'Layer_description'] = ''

    for row in df.itertuples():
      idx = row.Index
      if row.Layer_description not in ['', '. . ContainerConvLayer', 'ContainerSequential']:
        _, o, p, t = next(info_gen)
        df.at[idx, 'Output_dimensions'] = str(o)
        df.at[idx, 'Parameters'] =  p
        df.at[idx, 'Trainable'] = t
        if 'Conv2d' in row.Torch_class:
          df.at[idx, 'Currently'] = 'Unfrozen' if t else 'Frozen'

    # backfill container rows with summary layer information and layer/block counts
    # 1.set up index stores and counters
    m, b  = 0, 0
    layer_count = [0, 0, 0]                                       # layers in [div, child, blocks]
    block_count = [0, 0]                                          # blocks in [div, childs]
    frozen_count=[[0,0], [0, 0], [0,0]]                           # [Frozen, Unfrozen] layers in [div, child, blocks],

    # 2.iterate over rows, incrementing counters with each new row
    for row in df.itertuples():
      idx = row.Index
      if row.Currently == 'Frozen':
        for i in [0,1,2]: frozen_count[i][0] += 1
      if row.Currently == 'Unfrozen':
        for i in [0,1,2]: frozen_count[i][1] += 1
      if row.Layer_description != '':
        for i in [0,1,2]: layer_count[i] += 1

      # backfill 'Module' container rows with layer_info and block and layer counts
      if (row.Output_dimensions == '' and row.Container_child != '') or row.Module_name == '1':
        m = idx if m == 0 else m
        df.at[m, 'out_dim'] = df.at[idx-1, 'Output_dimensions']
        df.at[m, ['current', 'blk_chd', 'lyr_chd']] = self.get_frozen(frozen_count[1]), block_count[1], layer_count[1]
        m = idx
        layer_count[1] = block_count[1] = 0
        for i in [0, 1]: frozen_count[1][i] = 0

      # backfill 'Block' container rows with layer_info and layer counts
      if (row.Output_dimensions == '' and row.Container_block != '') or row.Module_name == '1':
        b = idx if b == 0 else b
        df.at[b, 'out_dim'] = df.at[idx-1, 'Output_dimensions'] or df.at[idx-2, 'Output_dimensions']
        df.at[b, ['current', 'lyr_blk']] = self.get_frozen(frozen_count[2]), layer_count[2]
        b = idx
        layer_count[2] = 0
        for i in [0, 1]: block_count[i] += 1
        for i in [0, 1]: frozen_count[2][i] = 0

    # 3.backfill division container rows with summary layer_info and block and layer counts
    div0_idx = df[df['Module_name'] == '0'].index.tolist()[0]
    div1_idx = df[df['Module_name'] == '1'].index.tolist()[0]

    df.at[div0_idx, 'out_dim'] = df.at[div1_idx-1, 'Output_dimensions'] or df.at[div1_idx-2, 'Output_dimensions']
    df.at[div0_idx, ['current', 'lyr_chd', 'blk_chd']] = self.get_frozen(frozen_count[0]), layer_count[0], block_count[0]

    df.at[div1_idx, 'out_dim'] = df.iloc[-1]['Output_dimensions']

    self._cndf = df


  def add_bs(self, dims):
    "Adds batch size `bs` to a list if layer dimensions `dims`"
    return [self.bs if i==0 else s for i, s in enumerate(dims)]

  @staticmethod
  def get_frozen(f):
    "Returns a string interpretation of the number of frozen/unfrozen layers in tuple `f`"
    if f[0] == 0: return 'Unfrozen'
    elif f[1] == 0: return 'Frozen'
    else: return f'{f[0]}/{(f[0]+f[1])} layers frozen'

  @property
  def output_dimensions(self):
    "Returns output dimensions of model (bs, classes)"
    return self._cndf.iloc[-1]['Output_dimensions']

  @property
  def frozen_to(self):
    "Returns parameter group model is curently frozen to"
    return self.learner.opt.frozen_idx + 1

  @property
  def num_param_groups(self):
    "Returns number of parameter groups"
    return len(self.learner.opt.param_groups)

  @property
  def batch_size(self):
    "Returns the batch size of the current learner"
    return self.bs

  @property
  def input_sizes(self):
    "Returns the sizes (dimensions bs, ch, h, w) of the model)"
    return self.inp_sz

  @property
  def model_info(self):
    "Return an info string derived from`Learner.model`"
    res = f"{self.model_type.capitalize()}: {self.model_name.capitalize()}\n"
    res += f"Input shape: {self.inp_sz} (bs, ch, h, w)\n"
    res += f"Output features: {self.output_dimensions} (bs, classes)\n"
    res += f"Currently frozen to parameter group {self.frozen_to} out of {self.num_param_groups}"
    return res

  @property
  def cndf(self):
    "Returns a ConvNav dataframe"
    return self._cndf.copy()

  @staticmethod
  def supported_models():
    "Prints list of supported models from 'models' list (imported from models)"
    print('Supported models')
    print('================\n')
    for d in models:
        [[print(m) for m, l in v] for k, v in d.items()]

# Cell
class CNDFView:
  "Class to view a CNDF dataframe"

  def copy_layerinfo(self, df):
    "Copy layer information and block/layer counts across from hidden columns to displayed columns"
    df.loc[df['Division'] == '', 'Division'] = df['div_id']
    df.loc[df['Container_child'] == '', 'Container_child'] = df['chd_id']
    df.loc[df['Container_block'] == '', 'Container_block'] = df['blk_id']
    df.loc[df['Output_dimensions'] == '', 'Output_dimensions'] = df['out_dim']
    df.loc[df['Currently'] == '', 'Currently'] = df['current']
    return df

  def check_view_args(self, df, truncate, verbose):
    "Check arguments given to view function, `df`, `truncate` and `verbose` are valid"
    assert type(df) == DataFrame and 'Module_name' in df.columns, "Not a valid convnav dataframe"
    assert isinstance(truncate, int) and -10 <= truncate <= 10, f"Argument 'truncate' must be an integer between -10 (show more cols) and +10 (show fewer cols)"
    assert isinstance(verbose, int) and 1 <= verbose <= 5, f"Argument verbose must be 1 2 or 3 "

  def view(self, df=None, verbose=3, tight=True, truncate=0, align_cols='left', top=False, show=True, return_df=False):
    "Display dataframe `df` with optional arguments and styling"

    if not show: return None
    _df = df if df is not None else self._cndf.copy()
    self.check_view_args(_df, truncate, verbose)

    if not isinstance(tight, bool): tight = True
    if len(_df) < 10: tight = False
    if verbose != 3: truncate = (10, 4, 0, 0, -10)[verbose-1]
    if verbose == 4: _df = self.copy_layerinfo(_df)

    post_msg = ''
    if top and len(_df) > 10:
      post_msg = f'...{len(_df)-10} more layers'
      _df = _df.iloc[:10]
      tight=False

    if len(_df) == 0:
      print('No data to display')
      return None

    with option_context("display.max_rows", 1000):
      _df.index.name = 'Index'
      _df_styled = _df.iloc[:,:-(11+truncate)].style.set_properties(**{'text-align': align_cols})
      if tight:
        display(_df_styled)
      else:
        display(_df.iloc[:,:-(11+truncate)])
    print(post_msg)
    if return_df and df is not None: return(_df)

  def copy_view(self, df, **kwargs):
    "Copy over layer information then call `view` to display dataframe"
    df = self.copy_layerinfo(df)
    self.view(df=df, **kwargs)

# Cell
class CNDFSearch:
  "Class to search a CNDF dataframe, display the results in a dataframe and returns matching module object(s)"

  def _find_layer(self, df, searchterm, exact):
    "Searches `df` for `searchterm`, returning exact matches only if `exact=True` otherwise any match"

    if isinstance(searchterm, int):
      assert searchterm >= 0 and searchterm <= len(df), f'Layer ID out of range: min 0, max {len(df)}'
      #select 'df' row using index from 'searchterm'
      x = df.iloc[searchterm].copy()
      x = DataFrame(x).transpose()
      return x

    #if searchterm is a float assume it is a layer name (i.e. format 0.0.1) and convert to string
    if isinstance(searchterm, float): searchterm = str(searchterm)

    if isinstance(searchterm, dict):
      #select rows matching the conditional df[key] ==/contains value (exact=True/false) for dict
      for col, s in searchterm.items():
        assert col in df.columns, f'{col} not a valid column identifier. Valid column names are {df.columns}'
        return df[df[col] == s].copy() if exact else df[df[col].str.contains(s)].copy()
      return x

    if isinstance(searchterm, str):
      #select rows in df where df[col] ==/contains searchterm string (exact=True/False)
      #returns results after first matches are found in a column (remining columns not searched)
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

  def search(self, searchterm, df=None, exact=True, show=True):
    "Search 'df` for single or combination of modules and layers. If df = None, searches instance dataframe `self._cndf` (default)"
    if df is not None:
      _df = df.copy()
    else:
       _df = df = self._cndf.copy()

    if isinstance(searchterm, float): searchterm = str(searchterm)

    if isinstance(searchterm, int):
      _df = self._find_layer(_df, searchterm, True)

    elif isinstance(searchterm, str):
      _df = self._find_layer(_df, searchterm, exact)

    elif isinstance(searchterm, dict):
      #concatenate successive search results (logical 'OR') for series of dicts
      _df = DataFrame()
      for col, s in searchterm.items():
        new_df = self._find_layer(df, {col:s}, exact)
        _df = pd.concat((_df, new_df), axis=0, ignore_index=False).drop_duplicates('Module_name')

    elif isinstance(searchterm, list):
      #concatenate successive search results (logical 'OR') in list
      _df = DataFrame()
      for s in searchterm:
        new_df = self._find_layer(df, s, exact)
        _df = pd.concat((_df, new_df), axis=0, ignore_index=False).drop_duplicates('Module_name')

    elif isinstance(searchterm, tuple):
      #recursively call find_layer on _df to logical 'AND' successive search results in tuple
      for s in searchterm:
        _df = self._find_layer(_df, s, exact)

    else: assert True, 'Unrecognizable searchterm'

    #show matches and return corresponding modules
    if _df is not None and not _df.empty:
      if show:
        print(f'{len(_df)} layers found matching searchterm(s): {searchterm}\n')
        self.view(df=_df)
      return _df['lyr_obj'].tolist()
    else:
      if show: print(f'No matches for searchterm(s): {searchterm}\n')
      return None

# Cell
class ConvNav(CNDF, CNDFSearch, CNDFView):
  "Class to view fastai supported CNNs, search and select module(s) and layer(s) for further investigation. Automatically builds a CNDF dataframe from Learner and Learner.summary()"
  def __init__(self, learner, learner_summary):
    super().__init__(learner, learner_summary)

  def __len__(self):
    return len(self._cndf)

  def __str__(self) -> str:
    return self.model_info

  def __call__(self):
    self.view(head=True)

  def __contains__(self, s):
    return self.search(s)

  @property
  def head(self):
    "Print `model` head summary info and modules"
    df = self._cndf.copy()
    df = df[df['Module_name'].str.startswith('1')]
    if not df.empty:
      res = f"{self.model_type.capitalize()}: {self.model_name.capitalize()}\n"
      res += f"Input shape: {self._cndf.iloc[1]['out_dim']} (bs, filt, h, w)\n"
      res += f"Output features: {self.output_dimensions} (bs, classes)\n"
      print(res)
      self.view(df, truncate=1)
    else:
      res = "Model has no head"
      print(res)

  @property
  def body(self):
    "Print `model` body summary info and modules"
    df = self._cndf.copy()
    df = df.loc[df['Module_name'].str.startswith('0')]
    if not df.empty:
      res = f"{self.model_type.capitalize()}: {self.model_name.capitalize()}\n"
      res += f"Input shape: {self.input_sizes} (bs, ch, h, w)\n"
      res += f"Output dimensions: {df.iloc[-1]['Output_dimensions']} (bs, filt, h, w)\n"
      res += f"Currently frozen to parameter group {self.frozen_to} out of {self.num_param_groups}\n"
      print(res)
      self.view(df)
    else:
      res = "Model body has no contents"
      print(res)

  @property
  def divs(self):
    "Print Summary information from `model` head and body"
    df = self._cndf[(self._cndf['Module_name'] == '0') | (self._cndf['Module_name'] == '1')].copy()

    for i in range(2):
      df_div = self._cndf.loc[self._cndf['div_id'] == str(i)].copy()
      df.iloc[i]['Model'] = self.model_name
      df.iloc[i]['Container_child'] = len(df_div[df_div['Container_child'] != ''])
      df.iloc[i]['Container_block'] = len(df_div[df_div['Container_block'] != ''])
      df.iloc[i]['Layer_description'] = len(df_div[df_div['Layer_description'] != ''])
      params = df_div['Parameters'].values
      params_summed = sum(filter(lambda i: isinstance(i, int), params))
      df.iloc[i]['Parameters'] = params_summed

    df['Output_dimensions'] = df['out_dim']
    df.iloc[0]['Currently'] = df.iloc[0]['current']

    df = df.rename(columns={'Container_child': 'Child modules', 'Container_block': 'Blocks', 'Layer_description': 'Layers'})
    print(f"{self.model_name.capitalize()}\nDivisions:  body (0), head (1)\n")
    self.view(df, tight=False)

  @property
  def dim_transitions(self):
    "Finds layers with different input and output dimensions. These are useful points to apply hooks and callbacks for investigating model activity."
    df = self._cndf[self._cndf['Torch_class'].str.contains('Conv2d')].copy()

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
    self.copy_view(df, tight=False)
    return df['lyr_obj'].tolist()

  @property
  def linear_layers(self):
    "Prints and returns all linear layers in the `model`"
    df = self._cndf[self._cndf['Torch_class'].str.contains('Linear')].copy()
    df['Division'] = df['div_id']

    print(f"{self.model_name.capitalize()} linear layers\n")
    self.view(df, truncate=1, tight=False)
    return df['lyr_obj'].tolist()

# Cell
def save_cndf(cn, filename, path='', with_modules=False):
  "Saves a CNDF dataframe of the ConvNav instance `cn` to persistent storage at `path` with `filename` gzip compresseed"
  if not with_modules: df = cn._cndf.iloc[:,:-1]
  with gzip.open(path+filename, "wb") as f:
    pickle.dump(df, f, pickle.HIGHEST_PROTOCOL)

# Cell
def load_cndf(filename, path=''):
  "Loads a CNDF dataframe from persistent storage at `path`+`filename` and unzips it"
  with gzip.open(path+filename, "rb") as f:
    return pickle.load(f)