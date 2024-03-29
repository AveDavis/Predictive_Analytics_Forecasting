# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/losses.ipynb.

# %% auto 0
__all__ = ['mae', 'mse', 'rmse', 'mape', 'smape', 'mase', 'rmae', 'quantile_loss', 'mqloss', 'coverage', 'calibration',
           'scaled_crps']

# %% ../nbs/losses.ipynb 2
from typing import Optional, Union

import numpy as np

# %% ../nbs/losses.ipynb 4
def _divide_no_nan(a: float, b: float) -> float:
    """
    Auxiliary funtion to handle divide by 0
    """
    div = a / b
    div[div != div] = 0.0
    div[div == float('inf')] = 0.0
    return div

# %% ../nbs/losses.ipynb 5
def _metric_protections(y: np.ndarray, y_hat: np.ndarray, weights: np.ndarray) -> None:
    assert (weights is None) or (np.sum(weights) > 0), 'Sum of weights cannot be 0'
    assert (weights is None) or (weights.shape == y.shape),\
        f'Wrong weight dimension weights.shape {weights.shape}, y.shape {y.shape}'

# %% ../nbs/losses.ipynb 8
def mae(y: np.ndarray, y_hat: np.ndarray,
        weights: Optional[np.ndarray] = None,
        axis: Optional[int] = None) -> Union[float, np.ndarray]:
    """
    
    Calculates Mean Absolute Error (MAE) between
    y and y_hat. MAE measures the relative prediction
    accuracy of a forecasting method by calculating the
    deviation of the prediction and the true
    value at a given time and averages these devations
    over the length of the series.
    
    $$ \mathrm{MAE}(\\mathbf{y}_{\\tau}, \\mathbf{\hat{y}}_{\\tau}) = 
        \\frac{1}{H} \\sum^{t+H}_{\\tau=t+1} 
        |y_{\\tau} - \hat{y}_{\\tau}| $$

        Parameters
        ----------
        y: numpy array. 
            Observed values.
        y_hat: numpy array
            Predicted values.
        weights: numpy array, optional. 
            Weights for weighted average.
        axis: None or int, optional. 
            Axis or axes along which to average a. 
            The default, axis=None, will average over all of the elements of 
            the input array. If axis is negative it counts from last to first.

        Returns
        -------
        mae: numpy array or double.
            Return the MAE along the specified axis.
    """
    _metric_protections(y, y_hat, weights)
    
    delta_y = np.abs(y - y_hat)
    if weights is not None:
        mae = np.average(delta_y[~np.isnan(delta_y)], 
                         weights=weights[~np.isnan(delta_y)],
                         axis=axis)
    else:
        mae = np.nanmean(delta_y, axis=axis)
        
    return mae

# %% ../nbs/losses.ipynb 11
def mse(y: np.ndarray, y_hat: np.ndarray, 
        weights: Optional[np.ndarray] = None,
        axis: Optional[int] = None) -> Union[float, np.ndarray]:
    """
    
    Calculates Mean Squared Error (MSE) between
    y and y_hat. MSE measures the relative prediction
    accuracy of a forecasting method by calculating the 
    squared deviation of the prediction and the true
    value at a given time, and averages these devations
    over the length of the series.
    
    $$ \mathrm{MSE}(\\mathbf{y}_{\\tau}, \\mathbf{\hat{y}}_{\\tau}) = 
        \\frac{1}{H} \\sum^{t+H}_{\\tau=t+1} (y_{\\tau} - \hat{y}_{\\tau})^{2} $$
    
        Parameters
        ----------
        y: numpy array.
            Actual test values.
        y_hat: numpy array.
            Predicted values.
        weights: numpy array, optional.
            Weights for weighted average.
        axis: None or int, optional.
            Axis or axes along which to average a. 
            The default, axis=None, will average over all of the 
            elements of the input array. If axis is negative it counts 
            from the last to the first axis.

        Returns
        -------
        mse: numpy array or double.
            Return the MSE along the specified axis.
    """
    _metric_protections(y, y_hat, weights)

    delta_y = np.square(y - y_hat)
    if weights is not None:
        mse = np.average(delta_y[~np.isnan(delta_y)], 
                         weights=weights[~np.isnan(delta_y)], 
                         axis=axis)
    else:
        mse = np.nanmean(delta_y, axis=axis)
        
    return mse

# %% ../nbs/losses.ipynb 14
def rmse(y: np.ndarray, y_hat: np.ndarray,
         weights: Optional[np.ndarray] = None,
         axis: Optional[int] = None) -> Union[float, np.ndarray]:
    """
    
    Calculates Root Mean Squared Error (RMSE) between
    y and y_hat. RMSE measures the relative prediction
    accuracy of a forecasting method by calculating the squared deviation
    of the prediction and the observed value at a given time and
    averages these devations over the length of the series.
    Finally the RMSE will be in the same scale
    as the original time series so its comparison with other
    series is possible only if they share a common scale. 
    RMSE has a direct connection to the L2 norm.
    
    $$ \mathrm{RMSE}(\\mathbf{y}_{\\tau}, \\mathbf{\hat{y}}_{\\tau}) = 
        \\sqrt{\\frac{1}{H} \\sum^{t+H}_{\\tau=t+1} (y_{\\tau} - \hat{y}_{\\tau})^{2}} $$
    
        Parameters
        ----------
        y: numpy array. 
            Observed values.
        y_hat: numpy array. 
            Predicted values.    
        weights: numpy array, optional. 
            Weights for weighted average.
        axis: None or int, optional. 
            Axis or axes along which to average a. 
            The default, axis=None, will average over all of the elements of 
            the input array. If axis is negative it counts from the last to first.

        Returns
        -------
        rmse: numpy array or double.
            Return the RMSE along the specified axis.
    """

    return np.sqrt(mse(y, y_hat, weights, axis))

# %% ../nbs/losses.ipynb 18
def mape(y: np.ndarray, y_hat: np.ndarray, 
         weights: Optional[np.ndarray] = None,
         axis: Optional[int] = None) -> Union[float, np.ndarray]:
    """
    
    Calculates Mean Absolute Percentage Error (MAPE) between
    y and y_hat. MAPE measures the relative prediction
    accuracy of a forecasting method by calculating the percentual deviation
    of the prediction and the observed value at a given time and
    averages these devations over the length of the series.
    The closer to zero an observed value is, the higher penalty MAPE loss
    assigns to the corresponding error.
    
    $$ \mathrm{MAPE}(\\mathbf{y}_{\\tau}, \\mathbf{\hat{y}}_{\\tau}) = 
        \\frac{1}{H} \\sum^{t+H}_{\\tau=t+1}
        \\frac{|y_{\\tau}-\hat{y}_{\\tau}|}{|y_{\\tau}|} $$
    
        Parameters
        ----------
        y: numpy array. 
            Observed values.
        y_hat: numpy array. 
            Predicted values.    
        weights: numpy array, optional. 
            Weights for weighted average.
        axis: None or int, optional. 
            Axis or axes along which to average a. 
            The default, axis=None, will average over all of the elements of 
            the input array. If axis is negative it counts from the last to first.

        Returns
        -------
        mape: numpy array or double.
            Return the MAPE along the specified axis.
    """
    _metric_protections(y, y_hat, weights)
        
    delta_y = np.abs(y - y_hat)
    scale = np.abs(y)
    mape = _divide_no_nan(delta_y, scale)
    mape = np.average(mape, weights=weights, axis=axis)
    mape = 100 * mape
    
    return mape

# %% ../nbs/losses.ipynb 21
def smape(y: np.ndarray, y_hat: np.ndarray,
          weights: Optional[np.ndarray] = None,
          axis: Optional[int] = None) -> Union[float, np.ndarray]:
    """
    
    Calculates Symmetric Mean Absolute Percentage Error (SMAPE) between
    y and y_hat. SMAPE measures the relative prediction
    accuracy of a forecasting method by calculating the relative deviation
    of the prediction and the observed value scaled by the sum of the
    absolute values for the prediction and observed value at a
    given time, then averages these devations over the length
    of the series. This allows the SMAPE to have bounds between
    0% and 200% which is desireble compared to normal MAPE that
    may be undetermined when the target is zero.
    
    $$ \mathrm{SMAPE}_{2}(\\mathbf{y}_{\\tau}, \\mathbf{\hat{y}}_{\\tau}) = 
       \\frac{1}{H} \\sum^{t+H}_{\\tau=t+1} 
       \\frac{|y_{\\tau}-\hat{y}_{\\tau}|}{|y_{\\tau}|+|\hat{y}_{\\tau}|} $$
    
        Parameters
        ----------
        y: numpy array. 
            Observed values.
        y_hat: numpy array. 
            Predicted values.    
        weights: numpy array, optional. 
            Weights for weighted average.
        axis: None or int, optional. 
            Axis or axes along which to average a. 
            The default, axis=None, will average over all of the elements of 
            the input array. If axis is negative it counts from the last to first.

        Returns
        -------
        smape: numpy array or double.
            Return the SMAPE along the specified axis.
    """
    _metric_protections(y, y_hat, weights)
        
    delta_y = np.abs(y - y_hat)
    scale = np.abs(y) + np.abs(y_hat)
    smape = _divide_no_nan(delta_y, scale)
    smape = 200 * np.average(smape, weights=weights, axis=axis)
    
    if isinstance(smape, float):
        assert smape <= 200, 'SMAPE should be lower than 200'
    else:
        assert all(smape <= 200), 'SMAPE should be lower than 200'
    
    return smape

# %% ../nbs/losses.ipynb 24
def mase(y: np.ndarray, y_hat: np.ndarray, 
         y_train: np.ndarray,
         seasonality: int,
         weights: Optional[np.ndarray] = None,
         axis: Optional[int] = None) -> Union[float, np.ndarray]:
    """
    
    Calculates the Mean Absolute Scaled Error (MASE) between
    y and y_hat. MASE measures the relative prediction
    accuracy of a forecasting method by comparinng the mean absolute errors
    of the prediction and the observed value against the mean
    absolute errors of the seasonal naive model.
    The MASE partially composed the Overall Weighted Average (OWA), 
    used in the M4 Competition.
    
    $$ \mathrm{MASE}(\\mathbf{y}_{\\tau}, \\mathbf{\hat{y}}_{\\tau}, \\mathbf{\hat{y}}^{season}_{\\tau}) = 
        \\frac{1}{H} \sum^{t+H}_{\\tau=t+1} \\frac{|y_{\\tau}-\hat{y}_{\\tau}|}{\mathrm{MAE}(\\mathbf{y}_{\\tau}, \\mathbf{\hat{y}}^{season}_{\\tau})} $$

        Parameters
        ----------
        y: numpy array. 
            Observed values.
        y_hat: numpy array. 
            Predicted values.   
        y_train: numpy array. 
            Actual insample Seasonal Naive predictions.
        seasonality: int.
            Main frequency of the time series;
            Hourly 24,  Daily 7, Weekly 52,
            Monthly 12, Quarterly 4, Yearly 1.
        weights: numpy array, optional. 
            Weights for weighted average.
        axis: None or int, optional. 
            Axis or axes along which to average a. 
            The default, axis=None, will average over all of the elements of 
            the input array. If axis is negative it counts from the last to first.

        Returns
        -------
        mase: numpy array or double.
            Return the mase along the specified axis.

        References
        ----------
        [1] https://robjhyndman.com/papers/mase.pdf
    """    
    delta_y = np.abs(y - y_hat)
    delta_y = np.average(delta_y, weights=weights, axis=axis)
    
    scale = np.abs(y_train[:-seasonality] - y_train[seasonality:])
    scale = np.average(scale, axis=axis)
    
    mase = delta_y / scale
    
    return mase

# %% ../nbs/losses.ipynb 27
def rmae(y: np.ndarray, 
         y_hat1: np.ndarray, y_hat2: np.ndarray, 
         weights: Optional[np.ndarray] = None,
         axis: Optional[int] = None) -> Union[float, np.ndarray]:
    """
            
    Calculates Relative Mean Absolute Error (RMAE) between
    two sets of forecasts (from two different forecasting methods).
    A number smaller than one implies that the forecast in the 
    numerator is better than the forecast in the denominator.
    
    $$ \mathrm{RMAE}(\\mathbf{y}_{\\tau}, \\mathbf{\hat{y}}_{\\tau}, \\mathbf{\hat{y}}^{base}_{\\tau}) = 
        \\frac{1}{H} \sum^{t+H}_{\\tau=t+1} \\frac{|y_{\\tau}-\hat{y}_{\\tau}|}{\mathrm{MAE}(\\mathbf{y}_{\\tau}, \\mathbf{\hat{y}}^{base}_{\\tau})} $$
    
        Parameters
        ----------
        y: numpy array. 
            Observed values.
        y_hat1: numpy array. 
            Predicted values of first model.
        y_hat2: numpy array. 
            Predicted values of baseline model.
        weights: numpy array, optional. 
            Weights for weighted average.
        axis: None or int, optional. 
            Axis or axes along which to average a. 
            The default, axis=None, will average over all of the elements of 
            the input array. If axis is negative it counts from the last to first.

        Returns
        -------
        rmae: numpy array or double.
            Return the RMAE along the specified axis.
    """
    numerator = mae(y=y, y_hat=y_hat1, weights=weights, axis=axis)
    denominator = mae(y=y, y_hat=y_hat2, weights=weights, axis=axis)
    rmae = numerator / denominator
    
    return rmae

# %% ../nbs/losses.ipynb 31
def quantile_loss(y: np.ndarray, y_hat: np.ndarray, q: float = 0.5, 
                  weights: Optional[np.ndarray] = None,
                  axis: Optional[int] = None) -> Union[float, np.ndarray]:
    """
    
    Computes the quantile loss (QL) between y and y_hat. 
    QL measures the deviation of a quantile forecast.
    By weighting the absolute deviation in a non symmetric way, the
    loss pays more attention to under or over estimation.    
    A common value for q is 0.5 for the deviation from the median.
    
    $$ \mathrm{QL}(\\mathbf{y}_{\\tau}, \\mathbf{\hat{y}}^{(q)}_{\\tau}) = 
        \\frac{1}{H} \\sum^{t+H}_{\\tau=t+1} 
        \Big( (1-q)\,( \hat{y}^{(q)}_{\\tau} - y_{\\tau} )_{+} 
        + q\,( y_{\\tau} - \hat{y}^{(q)}_{\\tau} )_{+} \Big) $$            
            
        Parameters
        ----------
        y: numpy array. 
            Observed values.
        y_hat: numpy array. 
            Predicted values.    
        q: float. 
            Quantile for the predictions' comparison.
        weights: numpy array, optional. 
            Weights for weighted average.
        axis: None or int, optional. 
            Axis or axes along which to average a. 
            The default, axis=None, will average over all of the elements of 
            the input array. If axis is negative it counts from the last to first.

        Returns
        -------
        quantile_loss: numpy array or double.
            Return the QL along the specified axis.
    """
    _metric_protections(y, y_hat, weights)

    delta_y = y - y_hat
    loss = np.maximum(q * delta_y, (q - 1) * delta_y)

    if weights is not None:
        quantile_loss = np.average(loss[~np.isnan(loss)], 
                             weights=weights[~np.isnan(loss)],
                             axis=axis)
    else:
        quantile_loss = np.nanmean(loss, axis=axis)
        
    return quantile_loss

# %% ../nbs/losses.ipynb 34
def mqloss(y: np.ndarray, y_hat: np.ndarray, 
           quantiles: np.ndarray, 
           weights: Optional[np.ndarray] = None,
           axis: Optional[int] = None) -> Union[float, np.ndarray]:
    """
    
    Calculates the Multi-Quantile loss (MQL) between y and y_hat. 
    MQL calculates the average multi-quantile Loss for
    a given set of quantiles, based on the absolute 
    difference between predicted quantiles and observed values.
        
    $$ \mathrm{MQL}(\\mathbf{y}_{\\tau},
                    [\\mathbf{\hat{y}}^{(q_{1})}_{\\tau}, ... ,\hat{y}^{(q_{n})}_{\\tau}]) = 
       \\frac{1}{n} \\sum_{q_{i}} \mathrm{QL}(\\mathbf{y}_{\\tau}, \\mathbf{\hat{y}}^{(q_{i})}_{\\tau}) $$
    
    The limit behavior of MQL allows to measure the accuracy 
    of a full predictive distribution $\mathbf{\hat{F}}_{\\tau}$ with 
    the continuous ranked probability score (CRPS). This can be achieved 
    through a numerical integration technique, that discretizes the quantiles 
    and treats the CRPS integral with a left Riemann approximation, averaging over 
    uniformly distanced quantiles.    
    
    $$ \mathrm{CRPS}(y_{\\tau}, \mathbf{\hat{F}}_{\\tau}) = 
        \int^{1}_{0} \mathrm{QL}(y_{\\tau}, \hat{y}^{(q)}_{\\tau}) dq $$          
            
        Parameters
        ----------
        y: numpy array. 
            Observed values.
        y_hat: numpy array. 
            Predicted values.    
        quantiles: numpy array. 
            Quantiles to compare against.
        weights: numpy array, optional. 
            Weights for weighted average.
        axis: None or int, optional. 
            Axis or axes along which to average a. 
            The default, axis=None, will average over all of the elements of 
            the input array. If axis is negative it counts from the last to first.

        Returns
        -------
        mqloss: numpy array or double.
            Return the MQL along the specified axis.
            
        References
        ----------
        [1] https://www.jstor.org/stable/2629907            
    """ 
    if weights is None: weights = np.ones(y.shape)
        
    _metric_protections(y, y_hat, weights)
    n_q = len(quantiles)
    
    y_rep  = np.expand_dims(y, axis=-1)
    error  = y_rep - y_hat
    mqloss = np.maximum(quantiles * error, (quantiles - 1) * error)
    
    # Match y/weights dimensions and compute weighted average
    weights = np.repeat(np.expand_dims(weights, axis=-1), repeats=n_q, axis=-1)
    mqloss  = np.average(mqloss, weights=weights, axis=axis)

    return mqloss

# %% ../nbs/losses.ipynb 37
def coverage(
        y: np.ndarray, y_hat_lo: np.ndarray, y_hat_hi: np.ndarray, 
    ) -> Union[float, np.ndarray]:
    """
    Calculates the coverage of y with y_hat_lo and y_hat_hi. 
    
        Parameters
        ----------
        y: numpy array. 
            Observed values.
        y_hat_lo: numpy array. 
            Lower prediction interval.
        y_hat_hi: numpy array. 
            Higher prediction interval.

        Returns
        -------
        coevrage: numpy array or double.
            Return the coverage of y_hat.
            
        References
        ----------
        [1] https://www.jstor.org/stable/2629907            
    """ 
    return 100 * np.logical_and(y>=y_hat_lo, y<=y_hat_hi).mean()

# %% ../nbs/losses.ipynb 39
def calibration(
        y: np.ndarray, y_hat_hi: np.ndarray, 
    ) -> Union[float, np.ndarray]:
    """
    Calculates the fraction of y that is lower than y_hat_hi. 
    
        Parameters
        ----------
        y: numpy array. 
            Observed values.
        y_hat_hi: numpy array. 
            Higher prediction interval.

        Returns
        -------
        coevrage: numpy array or double.
            Return the coverage of y_hat.
            
        References
        ----------
        [1] https://www.jstor.org/stable/2629907            
    """ 
    return (y<=y_hat_hi).mean()

# %% ../nbs/losses.ipynb 41
def scaled_crps(y: np.ndarray, y_hat: np.ndarray, 
                quantiles: np.ndarray, 
                weights: Optional[np.ndarray] = None,
                axis: Optional[int] = None) -> Union[float, np.ndarray]:
    """Scaled Continues Ranked Probability Score
    
    Calculates a scaled variation of the CRPS, as proposed by Rangapuram (2021),
    to measure the accuracy of predicted quantiles `y_hat` compared to the observation `y`.
    This metric averages percentual weighted absolute deviations as 
    defined by the quantile losses.
    
    $$ \mathrm{sCRPS}(\hat{F}_{\\tau}, \mathbf{y}_{\\tau}) = \\frac{2}{N} \sum_{i}
    \int^{1}_{0}
    \\frac{\mathrm{QL}(\hat{F}_{i,\\tau}, y_{i,\\tau})_{q}}{\sum_{i} | y_{i,\\tau} |} dq $$
    
    Where $\hat{F}_{\\tau}$ is the an estimated multivariate distribution, and $y_{i,\\tau}$
    are its realizations.        
            
        Parameters
        ----------
        y: numpy array. 
            Observed values.
        y_hat: numpy array. 
            Predicted values.    
        quantiles: numpy array. 
            Quantiles to compare against.
        weights: numpy array, optional. 
            Weights for weighted average.
        axis: None or int, optional. 
            Axis or axes along which to average a. 
            The default, axis=None, will average over all of the elements of 
            the input array. If axis is negative it counts from the last to first.

        Returns
        -------
        scaled_crps: numpy array or double.
            Return the scaled crps along the specified axis.
            
        References
        ----------
        [1] https://proceedings.mlr.press/v139/rangapuram21a.html      
    """ 
    eps = np.finfo(float).eps
    norm  = np.sum(np.abs(y))
    loss  = mqloss(y=y, y_hat=y_hat, quantiles=quantiles, weights=weights, axis=axis)
    loss  = 2 * loss * np.sum(np.ones(y.shape)) / (norm + eps)
    return loss
