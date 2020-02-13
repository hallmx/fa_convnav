# Welcome to fa_convnav
> CNN viewer and element selector.


fa_convnav works with the fastai deep learning library, allowing users to explore convolutional neural network (CNN)  structure and composition as well as select modules and layers for further investigation using pytorch hooks and fastai callbacks.  

fa_convnav provides native support for the following types of CNN model: 

* VGG
* alexnet
* resnets
* squeezenets
* densenets
* xresnets

With minor ammendments to the code, fa_convnav can be adapted for use with other CNN architectures and custom CNN models.

**A note about naming.** Naming conventions for the elements of a CNN is confusing. Here we adhere as closely as possible to that used by pytorch and fastai. 


*   **'layers'** are the processing units of the model, e.g. `conv2d`, `batchnorm2d`, `maxpool`, `relu` etc
*   **'modules'** may be layers but also container elements such as `cnn.sequential` or custom container elements such as resnet `BasicBlocks` or densenet `_DenseLayers`. Container modules can also contain the entire head or body of the model, or even the entire model.
*   **'container'** elements do not do any processing of information themselves but functionally group CNN submodules and layers together.
*   **'elements'** are all the elements that make up the CNN, both container and non-container layers and modules.
*  **'divisions'** refers to the head or body of a transfer learning model
*  **'model'** refers to a pre-trained architecture imported from the fastai library or custom architecture with a body and head structure. 
*  **architecture** is an untrained neural network


## Install


```
pip install fa_convnav
```


## Usage



First create deep learning vision project using a pretrained model downloaded from fastai, a pretrained model with custom head or a custom pytorch model. Creating a fastai2 vision project using a CNN and transfer learning is described in the [fastai documentation](https://dev.fast.ai/) and examples are given in examples00.ipynb and examples 01.ipynb. 

### Create and view a ConvNav dataframe.

```
from fa_convnav.navigator import *
```

With a fastai learner object `learner`, create a ConvNav instance from `learner` and `layer_info(learner)` method:

```
cn = ConvNav(learner, layer_info(learner)
```

The model type and name are automatically detected and a dataframe of CNN model information built. ConvNav dataframes combine an intuitive representation of the model architecture along with the description, class, output dimensions, parameters and frozen/unfrozen status of each module and layer.

View a ConvNav dataframe:

```
cn.view()
```

or 

```
cn() *prints just the first ten rows
```  

### Searching a ConvNav dataframe and selecting model elements

ConvNav dataframes can be searched and any element(s) (modules, blocks or layers) can be selected using ConvNav functions. 

*   Search for elements by module name, module type, layer description etc. Note that module names are those returned by the fastai named_modules() method. 
*   Select modules/layers individually, in blocks or by higher level containers, or by type of layer
*   View summaries of model head and body 

For example, 

```
cn.search('0.0.2', exact=True)
```

Searches for the module with module_name '0.0.2'. 

```
cn.spread(req='conv', num=8)
```

Returns eight conv2d layers equally spaced between the first and last modules of the model body.

```
cn.divs
```

Prints summary information for the model body and head. 

In most cases module/layer selections are displayed as a dataframe and the associated element objects returned for use with hooks and callbacks. 

## Examples


See the example notebooks, examples00.ipynb and examples01.ipynb, and for further description and code of how to use fa_convnav 

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
