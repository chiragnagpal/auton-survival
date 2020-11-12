# coding=utf-8
# MIT License

# Copyright (c) 2020 Carnegie Mellon University, Auton Lab

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


"""Loss function definitions for the Deep Survival Machines model

In this module we define the various losses for the censored and uncensored
instances of data corresponding to Weibull and LogNormal distributions.
These losses are optimized when training DSM.

.. todo::
  Use torch.distributions
.. warning::
  NOT DESIGNED TO BE CALLED DIRECTLY!!!

"""

import numpy as np
import torch
import torch.nn as nn


def _lognormal_loss(model, t, e):

  shape, scale = model.get_shape_scale()

  k_ = shape.expand(t.shape[0], -1)
  b_ = scale.expand(t.shape[0], -1)

  ll = 0.
  for g in range(model.k):

    mu = k_[:, g]
    sigma = b_[:, g]

    f = - sigma - 0.5*np.log(2*np.pi)
    f = f - torch.div((torch.log(t) - mu)**2, 2.*torch.exp(2*sigma))
    s = torch.div(torch.log(t) - mu, torch.exp(sigma)*np.sqrt(2))
    s = 0.5 - 0.5*torch.erf(s)
    s = torch.log(s)

    uncens = np.where(e == 1)[0]
    cens = np.where(e == 0)[0]
    ll += f[uncens].sum() + s[cens].sum()

  return -ll.mean()


def _weibull_loss(model, t, e):

  shape, scale = model.get_shape_scale()

  k_ = shape.expand(t.shape[0], -1)
  b_ = scale.expand(t.shape[0], -1)

  ll = 0.
  for g in range(model.k):

    k = k_[:, g]
    b = b_[:, g]

    s = - (torch.pow(torch.exp(b)*t, torch.exp(k)))
    f = k + b + ((torch.exp(k)-1)*(b+torch.log(t)))
    f = f + s

    uncens = np.where(e.cpu().data.numpy() == 1)[0]
    cens = np.where(e.cpu().data.numpy() == 0)[0]
    ll += f[uncens].sum() + s[cens].sum()

  return -ll.mean()


def unconditional_loss(model, t, e):

  if model.dist == 'Weibull':
    return _weibull_loss(model, t, e)
  elif model.dist == 'LogNormal':
    return _lognormal_loss(model, t, e)
  else:
    raise NotImplementedError('Distribution: '+model.dist+
                              ' not implemented yet.')

def _conditional_lognormal_loss(model, x, t, e, elbo=True):

  alpha = model.discount
  shape, scale, logits = model.forward(x)

  lossf = []
  losss = []

  k_ = shape
  b_ = scale

  for g in range(model.k):

    mu = k_[:, g]
    sigma = b_[:, g]

    f = - sigma - 0.5*np.log(2*np.pi)
    f = f - torch.div((torch.log(t) - mu)**2, 2.*torch.exp(2*sigma))
    s = torch.div(torch.log(t) - mu, torch.exp(sigma)*np.sqrt(2))
    s = 0.5 - 0.5*torch.erf(s)
    s = torch.log(s)

    lossf.append(f)
    losss.append(s)

  losss = torch.stack(losss, dim=1)
  lossf = torch.stack(lossf, dim=1)

  if elbo:

    lossg = nn.Softmax(dim=1)(logits)
    losss = lossg*losss
    lossf = lossg*lossf

    losss = losss.sum(dim=1)
    lossf = lossf.sum(dim=1)

  else:

    lossg = nn.LogSoftmax(dim=1)(logits)
    losss = lossg + losss
    lossf = lossg + lossf

    losss = torch.logsumexp(losss, dim=1)
    lossf = torch.logsumexp(lossf, dim=1)

  uncens = np.where(e.cpu().data.numpy() == 1)[0]
  cens = np.where(e.cpu().data.numpy() == 0)[0]
  ll = lossf[uncens].sum() + alpha*losss[cens].sum()

  return -ll.mean()


def _conditional_weibull_loss(model, x, t, e, elbo=True):

  alpha = model.discount
  shape, scale, logits = model.forward(x)

  k_ = shape
  b_ = scale

  lossf = []
  losss = []

  for g in range(model.k):

    k = k_[:, g]
    b = b_[:, g]

    s = - (torch.pow(torch.exp(b)*t, torch.exp(k)))
    f = k + b + ((torch.exp(k)-1)*(b+torch.log(t)))
    f = f + s

    lossf.append(f)
    losss.append(s)

  losss = torch.stack(losss, dim=1)
  lossf = torch.stack(lossf, dim=1)

  if elbo:

    lossg = nn.Softmax(dim=1)(logits)
    losss = lossg*losss
    lossf = lossg*lossf
    losss = losss.sum(dim=1)
    lossf = lossf.sum(dim=1)

  else:

    lossg = nn.LogSoftmax(dim=1)(logits)
    losss = lossg + losss
    lossf = lossg + lossf
    losss = torch.logsumexp(losss, dim=1)
    lossf = torch.logsumexp(lossf, dim=1)

  uncens = np.where(e.cpu().data.numpy() == 1)[0]
  cens = np.where(e.cpu().data.numpy() == 0)[0]
  ll = lossf[uncens].sum() + alpha*losss[cens].sum()

  return -ll.mean()


def conditional_loss(model, x, t, e, elbo=True):

  if model.dist == 'Weibull':
    return _conditional_weibull_loss(model, x, t, e, elbo)
  elif model.dist == 'LogNormal':
    return _conditional_lognormal_loss(model, x, t, e, elbo)
  else:
    raise NotImplementedError('Distribution: '+model.dist+
                              ' not implemented yet.')


def _weibull_cdf(model, x, t_horizon):

  squish = nn.LogSoftmax(dim=1)

  shape, scale, logits = model.forward(x)
  logits = squish(logits)

  k_ = shape
  b_ = scale

  t_horz = torch.tensor(t_horizon).double()
  t_horz = t_horz.repeat(shape.shape[0], 1)

  cdfs = []
  for j in range(len(t_horizon)):

    t = t_horz[:, j]
    lcdfs = []

    for g in range(model.k):

      k = k_[:, g]
      b = b_[:, g]
      s = - (torch.pow(torch.exp(b)*t, torch.exp(k)))
      lcdfs.append(s)

    lcdfs = torch.stack(lcdfs, dim=1)
    lcdfs = lcdfs+logits
    lcdfs = torch.logsumexp(lcdfs, dim=1)
    cdfs.append(lcdfs.detach().numpy())

  return cdfs


def _lognormal_cdf(model, x, t_horizon):

  squish = nn.LogSoftmax(dim=1)

  shape, scale, logits = model.forward(x)
  logits = squish(logits)

  k_ = shape
  b_ = scale

  t_horz = torch.tensor(t_horizon).double()
  t_horz = t_horz.repeat(shape.shape[0], 1)

  cdfs = []

  for j in range(len(t_horizon)):

    t = t_horz[:, j]
    lcdfs = []

    for g in range(model.k):

      mu = k_[:, g]
      sigma = b_[:, g]

      s = torch.div(torch.log(t) - mu, torch.exp(sigma)*np.sqrt(2))
      s = 0.5 - 0.5*torch.erf(s)
      s = torch.log(s)
      lcdfs.append(s)

    lcdfs = torch.stack(lcdfs, dim=1)
    lcdfs = lcdfs+logits
    lcdfs = torch.logsumexp(lcdfs, dim=1)
    cdfs.append(lcdfs.detach().numpy())

  return cdfs


def predict_cdf(model, x, t_horizon):
  torch.no_grad()
  if model.dist == 'Weibull':
    return _weibull_cdf(model, x, t_horizon)
  if model.dist == 'LogNormal':
    return _lognormal_cdf(model, x, t_horizon)
  else:
    raise NotImplementedError('Distribution: '+model.dist+
                              ' not implemented yet.')
