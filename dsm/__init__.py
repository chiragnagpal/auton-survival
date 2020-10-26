"""
Python package `dsm` provides an API to train the Deep Survival Machines
and associated models for problems in survival analysis. The underlying model
is implemented in `pytorch`.

What is Survival Analysis?
------------------------

**Survival Analysis** involves estimating when an event of interest, \( T \)
would take places given some features or covariates \( X \). In statistics
and ML these scenarious are modelled as regression to estimate the conditional
survival distribution, \( \mathbb{P}(T>t|X) \). As compared to typical
regression problems, Survival Analysis differs in two major ways:

* The Event distribution, \( T \) has positive support ie.
  \( T \in [0, \infty) \).
* There is presence of censoring ie. a large number of instances of data are
  lost to follow up.

Deep Survival Machines
----------------------

.. figure:: https://ndownloader.figshare.com/files/25259852
   :figwidth: 20 %
   :alt: map to buried treasure

   This is the caption of the figure (a simple paragraph).

**Deep Survival Machines (DSM)** is a fully parametric approach to model
Time-to-Event outcomes in the presence of Censoring first introduced in
[\[1\]](https://arxiv.org/abs/2003.01176).
In the context of Healthcare ML and Biostatistics, this is known as 'Survival
Analysis'. The key idea behind Deep Survival Machines is to model the
underlying event outcome distribution as a mixure of some fixed \( k \)
parametric distributions. The parameters of these mixture distributions as
well as the mixing weights are modelled using Neural Networks.

#### Usage Example
    >>> from dsm import DeepSurvivalMachines
    >>> model = DeepSurvivalMachines()
    >>> model.fit()
    >>> model.predict_risk()

Deep Recurrent Survival Machines
--------------------------------

**Deep Recurrent Survival Machines (DRSM)** builds on the original **DSM**
model and allows for learning of representations of the input covariates using
**Recurrent Neural Networks** like **LSTMs, GRUs**. Deep Recurrent Survival
Machines is a natural fit to model problems where there are time dependendent
covariates.

..warning:: Not Implemented Yet!

Deep Convolutional Survival Machines
------------------------------------

Predictive maintenance and medical imaging sometimes requires to work with
image streams. Deep Convolutional Survival Machines extends **DSM** and
**DRSM** to learn representations of the input image data using
convolutional layers. If working with streaming data, the learnt
representations are then passed through an LSTM to model temporal dependencies
before determining the underlying survival distributions.

..warning:: Not Implemented Yet!

References
----------

Please cite the following papers if you are using the `dsm` package.

[1] [Deep Survival Machines:
Fully Parametric Survival Regression and
Representation Learning for Censored Data with Competing Risks."
arXiv preprint arXiv:2003.01176 (2020)](https://arxiv.org/abs/2003.01176)</a>

```
  @article{nagpal2020deep,
  title={Deep Survival Machines: Fully Parametric Survival Regression and\
  Representation Learning for Censored Data with Competing Risks},
  author={Nagpal, Chirag and Li, Xinyu and Dubrawski, Artur},
  journal={arXiv preprint arXiv:2003.01176},
  year={2020}
  }
```

Compatibility
-------------
`dsm` requires `python` 3.5+ and `pytorch` 1.1+.

To evaluate performance using standard metrics
`dsm` requires `scikit-survival`.

Contributing
------------
`dsm` is [on GitHub]. Bug reports and pull requests are welcome.

[on GitHub]: https://github.com/chiragnagpal/deepsurvivalmachines

License
-------
Copyright 2020 [Chirag Nagpal](http://cs.cmu.edu/~chiragn),
[Auton Lab](http://www.autonlab.org).

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.



<img style="float: right;" width ="200px" src="https://www.cmu.edu/brand/downloads/assets/images/wordmarks-600x600-min.jpg">
<img style="float: right;padding-top:50px" src="https://www.autonlab.org/user/themes/auton/images/AutonLogo.png"> 

<br><br><br><br><br>
<br><br><br><br><br>


"""

from dsm.dsm_api import DeepSurvivalMachines, DeepRecurrentSurvivalMachines
