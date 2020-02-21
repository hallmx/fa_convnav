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

With minimal code changes, fa_convnav can also be adapted for use with other CNN architectures and custom CNN models.

**A note about naming.** Naming conventions for the elements of a CNN is confusing with many terms such as layer and module used interchangeably. Here we use the following definitions to describe a CNN. 


*   **'layers'** are the information processing units of the model, they can be single elements (e.g. `conv2d`, `batchnorm2d`, `maxpool`, `relu` etc) or for larger models with deeply nested sequences, a short sequence of elements wrapped in a container element. 
*   **'modules'** may be layers but also container elements, such as `nn.sequential`, which wrap a sequence of layers.
*   **'container'** elements group sequences of CNN layers or modules togather into functional units.
*   **'elements'** are all the elements that make up the CNN, both container and non-container,  layers and modules.
*  **'divisions'** refer to the head (1) and body (0)  of a transfer learning model
*  **'child containers'** are the first tier of nested modules. These usually match the modules returned with the fastai `model.named_children()` method. 
*   **'Blocks'** are the second tier of nested modules, usually repeating throughout the main bulk of the model and containing a fixed sequence of layers. Depending on the architecture, blocks may have a specific name such as `BasicBlock` or `_DenseBlock`.
*  **'model'** refers to a pre-trained architecture with head and body divisions. 
*  **architecture** is an untrained neural network


## Install


```
pip install fa_convnav
```


## How to Use



First set up a deep learning vision project using fastai2 and create a Learner object from a dataloader, pretrained model and an optimizer. All the pretrained models installed with the fastai2 library are supported by fa_convnav. Run `convnav_supported_models()` in a notebook cell to see the complete list. 

If you are not familiar with the fastai/fastai2 library then the [fastai documentation](https://dev.fast.ai/) or most recent[Deep Learning for Coders](https://course.fast.ai/index.html) course are excellent places to start. Alternatively to quickly get a feel for and play around with fastai2 and fa_convnav see the example notebooks, `03_examples00.ipynb` and `04_examples 01.ipynb` in this repo. 

## Create and view a ConvNav dataframe.

```
from fa_convnav.navigator import *
```

With a fastai Learner object `Learner`, create a ConvNav instance `cn`:

```
cn = ConvNav(learner, Learner.summary())
```

The model type and name are automatically detected and a dataframe of CNN model information built. We will call this a CNDF dataframe. CNDF dataframes combine an intuitive representation of the model architecture along with the description, class, output dimensions, parameters and frozen/unfrozen status of each module and layer.

View a CNDF dataframe:

```
cn.view()
```

or 

```
cn() *prints just the first ten rows
```  

## Searching a CNDF dataframe and selecting model elements

CNDF dataframes can be viewed whole to see the overall structure of the model as well as subsetted and/or searched for any combination of model element(s). The selected element(s) are displayed and the module objects returned for further use, for example as targets for pytorch hooks and fastai callbacks. CNDF dataframes can also be saved to persistent storage. 

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
Searches for, displays and returns the module objects for eight `Conv2d` layers equally spaced from start to end of the model.



## Example notebooks


Find `03_examples00.ipynb` and `04_examples01.ipynb` in this repo. These contain working examples of fa_convnav used to view a resnet model and select appropriate modules for use in investigating model training. Example notebooks can be downloaded and run in any notebook environment. 

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
