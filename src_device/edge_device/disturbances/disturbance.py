import numpy as np
from abc import ABC, abstractmethod


class Disturbance(ABC):

  def __init__(self, disturbance_type: str, digit: int = 2, **kwargs):
    ''' Parameters
        ----------
        disturbance_type:  The type of disturbance e.g., white_noise, random_spike, drift.
        digit:             The number of digits to round the disturbance to.
    '''
    self.disturbance_type = disturbance_type
    self.digit = digit
    self.parameters = kwargs

  @abstractmethod
  def simulate(self) -> float:
    pass


class WhiteNoise(Disturbance):
  ''' White noise disturbance. '''
  disturbance_type = 'white_noise'

  def __init__(self, **kwargs):
    ''' Parameters
        ----------
        mean:  The mean of the white noise.
        std:   The standard deviation of the white noise.
    '''
    super().__init__(disturbance_type=self.disturbance_type, **kwargs)
    self.mean = kwargs.get('mean', 0)
    self.std = kwargs.get('std', 1)

  def simulate(self) -> dict:
    return round(np.random.normal(self.mean, self.std), self.digit)


class RandomSpike(Disturbance):
  ''' Random spike disturbance. '''
  disturbance_type = 'random_spike'

  def __init__(self, **kwargs):
    ''' Parameters
        ----------
        probability:  The probability of a spike occurring.
        spike_range:  The range of the spike.
    '''
    super().__init__(disturbance_type=self.disturbance_type, **kwargs)
    self.probability = self.parameters.get('probability', 0.1)
    if not 0 <= self.probability <= 1:
      raise ValueError('Probability must be between 0 and 1.')
    self.spike_range = self.parameters.get('spike_range', (-1, 1))

  def simulate(self) -> float:
    ''' Simulates a random spike within the specified range based on the spike probability. '''
    if np.random.random() < self.probability:
      return round(np.random.uniform(*self.spike_range), self.digit)
    return 0


class Drift(Disturbance):
  '''  Drift disturbance that increases or decreases linearly over time. '''
  disturbance_type = 'drift'

  def __init__(self, **kwargs):
    ''' Parameters
        ----------
        rate:  The rate of change (e.g., +0.01 per simulation step).
        start: The initial value of the drift.
    '''
    super().__init__(disturbance_type=self.disturbance_type, **kwargs)
    self.rate = kwargs.get('rate', 0.01)
    self.current_value = kwargs.get('start', 0)

  def simulate(self) -> float:
    ''' Simulate the current value of the drift and increment it. '''
    self.current_value += self.rate
    return round(self.current_value, self.digit)


def parse_disturbances(data: dict) -> list[Disturbance]:
  ''' Parse disturbances from the input data. 

      Parameters
      ----------
      data:  The input data containing the disturbances.
  '''
  disturbances = []
  for disturbance in data.get('disturbances', []):
    disturbance_type = disturbance['disturbance_type']
    parameters = disturbance['parameters']
    if disturbance_type == 'white_noise':
      disturbances.append(WhiteNoise(**parameters))
    elif disturbance_type == 'random_spike':
      disturbances.append(RandomSpike(**parameters))
    elif disturbance_type == 'drift':
      disturbances.append(Drift(**parameters))
    else:
      raise ValueError(f'Unknown disturbance type: {disturbance_type}')
  return disturbances
