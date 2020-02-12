# Welcome to fa_ConvNav
> CNN viewer and element selector.


fa_ConvNav works with the fastai deep learning library. It allows users to create a dataframe representation of a model to explore model structure and composition then select layers or groups of layers in divisions, modules or blocks for display and/or using as elements for further model investigation using hooks and callbacks.  

fa_ConvNav supports all the models used for transfer learning imported with the fastai library: 

*  `VGG`
* `alexnet`
* `resnets`
* `squeezenets`
* `densenets`
* `xresnets`

It is quite possible fa_ConvNav can be made to work using other models, and outside of fastai, with some ammendments to the code but thus far, this has not yet been implemented. 
<br /><br />

**A note about naming.** The naming conventions for the elemenst of a CNN is confusing. Here we adhere as closely as possible to that used by pytorch and fastai. 


*   **'layers'** are the processing units of the model, e.g. `conv2d`, `batchnorm2d`, `maxpool`, `relu` etc
*   **'modules'** may be layers but also container elements such as `cnn.sequentia`l or custom container elements such as resnet `Basicblocks` or densnet` _DenseLayers`. Container modules can contain the entire head or body of the model, or the entire model itself.
*   **'container'** elements do not do any processing of information themsleves but act as a means of structuring the CNN into functional groupings with a common input and output. 
*   **'elements'** are all the elements that make up the CNN, both container and non-container layers and modules.
*  **'divisions'** refers to the head or body of the model
*  **'model'** refers to a trained architecture imported from the fastai library or custom architecture with a body and head structure. 





## Install


`pip install fa_ConvNav`


## Usage

### With fastai

fa_ComvNav requires fastai2 to be installed as it uses a fatsai2 learner object and the result of a layer_info() method call to obtain the required model imformation. To use, therefore, first create a project with fastai2 and create a `learner` object from a datasource as described in the [fastai documentation](https://dev.fast.ai/). 

### Create and view a ConvNav dataframe.

`from fa_ConvNav.navigator import *`

Create a ConvNav object from a fastai learner and the fastai layer_info(learner) method:

`cn = ConvNav(learner, layer_info(learner)`
<br /><br />

The model type and name are automatically detected and a dataframe of model information constructed. ConvNav dataframes combine an intuitive representation of the model architecture along with the description, class, output dimensions, parameters and frozen/unfrozen status of each layer and, where appropriate, module. 
<br /><br />

View a ConvNav dataframe:

`cn.view()`

or 

`cn()`  *prints just the first ten rows

### Searching a ConvNav dataframe and selecting model elements

ConvNav dataframes can be searched and any element(s) (modules, blocks or layers) can be selected using ConvNav functions. 

*   Search for elements by module name (c.f. `fastai model.named_modules()`, module type, layer description etc
*   Select modules/layers individually, in blocks or by higher level containers, or by type of layer
*   View summaries of model head and body 

For example, 

`cn.search('0.0.2', exact+True)`

Searches for the module with module_name '0.0.2'. 

`cn.spread(req='conv', num=8)`

Returns eight conv2d layers equally spaced across the model body.

`cn.divs`

Prints summary information for the major divisions of the model - the body and head. 

>>Where specific selections are made the selection is dipslayed as a dataframe and the element objects are returned for use with hooks and callbacks. 

## Examples


Examples of fa_convnav being used with fastai2 are given in examples00.ipynb and examples01.ipynb

## Tests

To run test in parallel launch:
`nbdev_test_nbs` from the command line 
or
`!nbdev_test_nbs` from inside a Jupyter Notebook with nbdev installed

## Docs

This project, it's github repo and documentation were all built using the fastai nbdev literate programming environment for Jupyter Notebooks. Find out more about nbdev and use it in your own project [here](https://github.com/fastai/nbdev)

## Contributing

After you clone this repository, please run nbdev_install_git_hooks in your terminal. This sets up git hooks, which clean up the notebooks to remove the extraneous stuff stored in the notebooks (e.g. which cells you ran) which causes unnecessary merge conflicts.

Before submitting a PR, check that the local library and notebooks match. The script nbdev_diff_nbs can let you know if there is a difference between the local library and the notebooks.

If you made a change to the notebooks in one of the exported cells, you can export it to the library with nbdev_build_lib or make fastai2.
If you made a change to the library, you can export it back to the notebooks with nbdev_update_lib.
