#  Copyright 2021-present, the Recognai S.L. team.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Callable, Dict, Hashable, List, Tuple, Union

import pandas as pd
from pydantic import BaseModel

if TYPE_CHECKING:
    from argilla.client.feedback.dataset import FeedbackDataset


# Type aliases
Responses = List[Union[float, int, str]]
Suggestions = Responses
# Expected format for the nltk's AnnotationTask
FormattedResponses = List[Tuple[Any, Hashable, Hashable]]


class MetricResultBase(BaseModel):
    """Base class for the result of a metric."""

    metric_name: str


class AgreementMetricResult(MetricResultBase):
    """Container for the result of an agreement metric.

    It contains two fields, `metric_name` and `result` with the value of the metric.
    """

    result: float


class AnnotatorMetricResult(MetricResultBase):
    """Container for the result of an annotator metric.

    It contains two fields, `metric_name` and `result` with the value of the metric.
    """

    result: Union[float, Dict[str, float], pd.DataFrame, List[pd.DataFrame]]

    class Config:
        arbitrary_types_allowed = True


class AnnotatorMetricBase(ABC):
    """Base class for Annotator metrics."""

    def __init__(self, responses: Responses = None, suggestions: Suggestions = None) -> None:
        """
        Args:
            responses: Responses given by the user.
                Depending on the type of question it can be a list of strings, or integers.
            suggestions: Suggestions offered for the annotators.
                Same format as `responses`.
        """
        self._responses = responses
        self._suggestions = suggestions

    def compute(self, **kwargs):
        responses, suggestions = self._pre_process(self._responses, self._suggestions)
        return self._compute(responses, suggestions, **kwargs)

    def _pre_process(self, responses: Responses, suggestions: Suggestions) -> Any:
        """Optional data preprocessing. By default it just passes the data to the _compute method.

        Args:
            responses: Responses given by the user.
            suggestions: Suggestions offered for the annotators.

        Returns:
            data: tuple with the preprocessed data.
        """
        return responses, suggestions

    @abstractmethod
    def _compute(self, responses: Responses, suggestions: Suggestions, **kwargs):
        """Abstract method where the computation is done.

        Args:
            responses: Responses given by the user, as expected by the given metric.
            suggestions: Suggestions offered for the annotators, as expected by the given metric.
        """
        pass


class AnnotationTaskMetricBase(ABC):
    """Base class for Agreement metrics."""

    def __init__(self, annotated_dataset: FormattedResponses = None, distance_function: Callable = lambda x: x) -> None:
        """
        Args:
            annotated_dataset: Annotated dataset as expected by the metric.
            distance_function: Distance function to use for the metric.
                Depending on the type of data we need a function to compute the distance.
                For example for binary data we can use the binary distance function,
                while RatingQuestion works with an interval distance as we are dealing with
                numeric values.
        """
        self._dataset = annotated_dataset
        self._distance_function = distance_function

    def compute(self, **kwargs) -> float:
        """General method to obtain the metric.

        Args:
            kwargs: Optional arguments that could be passed to the metric.

        Returns:
            metric: Metric result that will be stored in the `AgreementMetricResult`.
        """
        data = self._pre_process(self._dataset)
        return self._compute(data, **kwargs)

    def _pre_process(self, data: FormattedResponses, **kwargs) -> Any:
        """Optional data preprocessing. By default it just passes the data to the _compute method.

        Args:
            data: annotated dataset.
            kwargs: optional arguments to be passed to the metric.

        Returns:
            data: dataset prepared for the _compute method.
        """
        return data

    @abstractmethod
    def _compute(self, data: FormattedResponses, **kwargs):
        """Abstract method where the computation is done.

        Args:
            data: Data as expected for the given metric.
        """
        pass


class MetricBase:
    _metrics_per_question: Dict[str, Callable] = {}

    def __init__(self, dataset: "FeedbackDataset", question_name: str) -> None:
        """Initializes a `AgreementMetric` object to compute agreement metrics on
        a `FeedbackDataset` for a given question.

        Args:
            dataset: FeedbackDataset to compute the metrics.
            question_name: Name of the question for which we want to analyse the agreement.

        Raises:
            NotImplementedError: If the question type is not supported.
        """
        self._dataset = dataset
        self._question_name = question_name
        self._question_type = type(self._dataset.question_by_name(question_name))
        if allowed_metrics := self._metrics_per_question.get(self._question_type):
            self._allowed_metrics = allowed_metrics
        else:
            raise NotImplementedError(f"No metrics are defined currently for {self._question_type.__name__}")

    @property
    def allowed_metrics(self) -> List[str]:
        """Available metrics for the given question."""
        return list(self._allowed_metrics)