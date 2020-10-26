# coding=utf-8
# Copyright 2020 Chirag Nagpal, Auton Lab.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This module is a wrapper around torch implementations and
provides a convenient API to train Deep Survival Machines.
"""

from dsm.dsm_torch import DeepSurvivalMachinesTorch
from dsm.losses import predict_cdf
from dsm.utilities import train_dsm

import torch

import numpy as np

class DeepSurvivalMachines():
  """A Deep Survival Machines model.

  This is the main interface to a Deep Survival Machines model.
  A model is instantiated with approporiate set of hyperparameters and
  fit on numpy arrays consisting of the features, event/censoring times
  and the event/censoring indicators.

  For full details on Deep Survival Machines, refer to our paper [1].

  References
  ----------
  [1] <a href="https://arxiv.org/abs/2003.01176">Deep Survival Machines:
  Fully Parametric Survival Regression and
  Representation Learning for Censored Data with Competing Risks."
  arXiv preprint arXiv:2003.01176 (2020)</a>

  Parameters
  ----------
  k: int
      The number of underlying parametric distributions.
  layers: list
      A list of integers consisting of the number of neurons in each
      hidden layer.
  distribution: str
      Choice of the underlying survival distributions.
      One of 'Weibull', 'LogNormal'.
      Default is 'Weibull'.
  temp: float
      The logits for the gate are rescaled with this value.
      Default is 1000.
  discount: float
      a float in [0,1] that determines how to discount the tail bias
      from the uncensored instances.
      Default is 1.

  Example
  -------
  >>> from dsm import DeepSurvivalMachines
  >>> model = DeepSurvivalMachines()
  >>> model.fit(x, t, e)

  """

  def __init__(self, k=3, layers=None, distribution="Weibull",
               temp=1000., discount=1.0):
    super(DeepSurvivalMachines, self).__init__()

    self.k = k
    self.layers = layers
    self.dist = distribution
    self.temp = temp
    self.discount = discount
    self.fitted = False

  def __call__(self):
    if self.fitted:
      print("A fitted instance of the Deep Survival Machines model")
    else:
      print("An unfitted instance of the Deep Survival Machines model")

    print("Number of underlying distributions (k):", self.k)
    print("Hidden Layers:", self.layers)
    print("Distribution Choice:", self.dist)


  def fit(self, x, t, e, vsize=0.15, 
          iters=1, learning_rate=1e-3, batch_size=100,
          elbo=True, optimizer="Adam", random_state=100):

    """This method is used to train an instance of the DSM model.

    Parameters
    ----------
    x: np.ndarray
        A numpy array of the input features, \( x \).
    t: np.ndarray
        A numpy array of the event/censoring times, \( t \).
    e: np.ndarray
        A numpy array of the event/censoring indicators, \( \delta \).

        \( \delta = 1 \) means the event took place.
    vsize: float
        Amount of data to set aside as the validation set.
    iters: int
        The maximum number of training iterations on the training dataset.
    learning_rate: float
        The learning rate for the `Adam` optimizer.
    batch_size: int
        learning is performed on mini-batches of input data. this parameter
        specifies the size of each mini-batch.
    elbo: bool
        Whether to use the Evidence Lower Bound for Optimization.
        Default is True.
    optimizer: str
        The choice of the gradient based optimization method. One of 
        'Adam', 'RMSProp' or 'SGD'.
    random_state: float
        random seed that determines how the validation set is chosen.
    """

    idx = list(range(x.shape[0]))
    np.random.seed(random_state)
    np.random.shuffle(idx)
    x_train, t_train, e_train = x[idx], t[idx], e[idx]

    x_train = torch.from_numpy(x_train).double()
    t_train = torch.from_numpy(t_train).double()
    e_train = torch.from_numpy(e_train).double()

    vsize = int(vsize*x_train.shape[0])

    x_val, t_val, e_val = x_train[-vsize:], t_train[-vsize:], e_train[-vsize:]
    x_train = x_train[:-vsize]
    t_train = t_train[:-vsize]
    e_train = e_train[:-vsize]

    inputdim = x_train.shape[1]

    if type(self).__name__ == "DeepSurvivalMachines":

      model = DeepSurvivalMachinesTorch(inputdim,
                                        k=self.k,
                                        layers=self.layers,
                                        init=False, 
                                        dist=self.dist,
                                        temp=self.temp,
                                        discount=self.discount,
                                        optimizer=optimizer)

      model, _ = train_dsm(model, x_train, t_train, e_train,
                           x_val, t_val, e_val,
                           n_iter=iters,
                           lr=learning_rate,
                           elbo=elbo,
                           bs=batch_size)

      self.torch_model = model.eval()
      self.fitted = True

    else:
      raise NotImplementedError("`fit` nethod not implemented for "+
                                type(self).__name__)


  def predict_risk(self, x, t):
    """Returns the estimated risk of an event occuring before time \( t \)
      \( \widehat{\mathbb{P}}(T\leq t|X) \) for some input data \( x \).

    Parameters
    ----------
    x: np.ndarray
        A numpy array of the input features, \( x \).
    t: list or float
        a list or float of the times at which survival probability is
        to be computed
    Returns:
      np.array: numpy array of the risks at each time in t.
    """

    if self.fitted:
      return 1-self.predict_survival(x, t)

    else:
      raise Exception("The model has not been fitted yet. Please fit the " +
                      "model using the `fit` method on some training data " +
                      "before calling `predict_survival`.")


  def predict_survival(self, x, t):
    """Returns the estimated survival probability at time \( t \),
      \( \widehat{\mathbb{P}}(T > t|X) \) for some input data \( x \).

    Parameters
    ----------
    x: np.ndarray
        A numpy array of the input features, \( x \).
    t: list or float
        a list or float of the times at which survival probability is
        to be computed
    Returns:
      np.array: numpy array of the survival probabilites at each time in t.
    """

    if not isinstance(t, list):
      t = [t]

    if self.fitted:
      x = torch.from_numpy(x)
      scores = predict_cdf(self.torch_model, x, t)
      return np.exp(np.array(scores)).T

    else:
      raise Exception("The model has not been fitted yet. Please fit the " +
                      "model using the `fit` method on some training data " +
                      "before calling `predict_risk`.")

class DeepRecurrentSurvivalMachines(DeepSurvivalMachines):
  __doc__ = "..warning:: Not Implemented"
  pass

class DeepConvolutionalSurvivalMachines(DeepRecurrentSurvivalMachines):
  __doc__ = "..warning:: Not Implemented"
  pass
