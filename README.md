# Welcome to fa_convnav
> CNN viewer and element selector.


fa_convnav works with the fastai deep learning library, allowing users to explore convolutional neural network (CNN)  structure and composition as well as select modules and layers for further investigation using hooks and callbacks.  

fa_convnav provides native support for the following types of CNN model: 

* VGG
* alexnet
* resnets
* squeezenets
* densenets
* xresnets

With minor ammendments to the code, fa_convnav can be adapted for use with other CNN architectures and custom CNN models.

**A note about naming.** Naming conventions for the elements of a CNN is confusing with many terms such as layer nd module used interchangeably. Here use the following set of definitions to describe the lements of a CNN. 


*   **'layers'** are the information processing units of the model, they can be single elemenst (e.g. `conv2d`, `batchnorm2d`, `maxpool`, `relu` etc) or for larger models with deeply nested sequences, a short sequence of elements wrapped in a container element. 
*   **'modules'** may be layers but also container elements wrapping a sequence of layers such as `cnn.sequential`.
*   **'container'** elements do not do any information processing themselves but group sequences of CNN layers or modules togather into functional units.
*   **'elements'** are all the elements that make up the CNN, both container and non-container,  layers and modules.
*  **'divisions'** refer to the head and body of a transfer learning model
*  **'child containers'** the first tier of nested modules. As far as possble these match the modules returned with the fastai `model.named_children()` method. 
*   **'Blocks'** are the second tier of nested modules usually containing a repeating sequence of layers and given a specific name such as `BasicBlock` or `_DenseBlock`
*  **'model'** refers to a pre-trained architecture imported from the fastai library or custom architecture with a body and head structure. 
*  **architecture** is an untrained neural network


## Install


```
pip install fa_convnav
```


## Usage



First create a deep learning vision project using fastai2 and one of the pretrained models supported by fa_convnav (see above or run `supported_models()` in a notebook cell). All the transfer learning models that come ready to download and use with the fastai2 library are supported by fa_convnav.  Creating a fastai2 vision project using a CNN and transfer learning is described in the [fastai documentation](https://dev.fast.ai/). To quickly get started and play around with fa_convnav see the example notebooks, examples00.ipynb and examples 01.ipynb. 

### Create and view a ConvNav dataframe.

```
from fa_convnav.navigator import *
```

With a fastai Learner object `Learner`, create a ConvNav instance `cn`:

```
cn = ConvNav(learner, Learner.summary())
```

The model type and name are automatically detected and a dataframe of CNN model information built. We will call this dataframe as a CNDF dataframe. CNDF dataframes combine an intuitive representation of the model architecture along with the description, class, output dimensions, parameters and frozen/unfrozen status of each module and layer.

View a CNDF dataframe:

```
cn.view()
```

or 

```
cn() *prints just the first ten rows
```  

### Searching a CNDF dataframe and selecting model elements

CNDF dataframes can be viewed whole to see the overall structure of the model as well as subsetted and/or searched for any combination of model element(s). Selected elements are returned with associated module objects for use with Pytorch hooks and fastai callbacks. CNDF dataframes can be saved and loaded from to persistent storage. 

For example:

```
cn.divs
```

Displays summary information for the model body and head. 

```
cn.search('0.0.2', exact=True)
```

Searches for, displays and returns the module object with module_name '0.0.2'. 

```
cn.spread(req='conv', num=8)
```
Searches for, displays and returns the module objects for 8 con2d layers equally spaced from start to end of the model.



## Examples


Example notebooks examples00.ipynb and examples01.ipynb contain working examples of fa_convnav being used with a resnet model. Example notebooks can be downloaded and run in any notebook environment. 

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
