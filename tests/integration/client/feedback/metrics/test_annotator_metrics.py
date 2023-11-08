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

import uuid
from typing import TYPE_CHECKING, List, Union

import pytest
from argilla.client.feedback.dataset import FeedbackDataset
from argilla.client.feedback.metrics import AnnotatorMetric, AnnotatorMetricResult
from argilla.client.feedback.metrics.annotator_metrics import get_responses_per_user
from argilla.client.feedback.schemas import (
    FeedbackRecord,
    LabelQuestion,
    MultiLabelQuestion,
)

if TYPE_CHECKING:
    from argilla.client.feedback.schemas.types import AllowedFieldTypes, AllowedQuestionTypes


@pytest.mark.parametrize(
    "question, metric_names",
    [
        # TextQuestion
        # ("question-1", "gleu"),
        # RatingQuestion
        ("question-2", ["accuracy", "spearman-r"]),
        # LabelQuestion
        ("question-3", "accuracy"),
        ("question-3", ["precision", "f1-score"]),
        # No current implementation for MultiLabelQuestion
        ("question-4", "accuracy"),
        # RankingQuestion
        ("question-5", "accuracy"),
    ],
)
@pytest.mark.usefixtures(
    "feedback_dataset_guidelines",
    "feedback_dataset_fields",
    "feedback_dataset_questions",
    "feedback_dataset_records_with_paired_suggestions",
)
def test_annotator_metric(
    feedback_dataset_guidelines: str,
    feedback_dataset_fields: List["AllowedFieldTypes"],
    feedback_dataset_questions: List["AllowedQuestionTypes"],
    feedback_dataset_records_with_paired_suggestions: List[FeedbackRecord],
    question: str,
    metric_names: Union[str, List[str]],
):
    dataset = FeedbackDataset(
        guidelines=feedback_dataset_guidelines,
        fields=feedback_dataset_fields,
        questions=feedback_dataset_questions,
    )
    dataset.add_records(records=feedback_dataset_records_with_paired_suggestions)

    if question in ("question-4", "question-5"):
        with pytest.raises(NotImplementedError):
            AnnotatorMetric(dataset, question)
    else:
        metric = AnnotatorMetric(dataset, question)
        metrics_report = metric.compute(metric_names)
        assert len(metrics_report) == 3  # Number of annotators
        assert isinstance(metrics_report, dict)
        user_id = str(uuid.UUID(int=1))
        metric_results = metrics_report[user_id]
        assert isinstance(metric_results, list)
        metric_result = metric_results[0]
        assert isinstance(metric_result, AnnotatorMetricResult)
        if isinstance(metric_names, str):
            metric_names = [metric_names]

        assert all([result.metric_name == name for result, name in zip(metric_results, metric_names)])
        # TODO: Check some values for the metrics


@pytest.mark.parametrize(
    "question, status, num_responses",
    [
        ("question-1", "submitted", 4),
        ("question-2", "submitted", 4),
        ("question-3", "submitted", 4),
        ("question-4", "submitted", 4),
        ("question-5", "submitted", 4),
        ("question-1", "draft", 0),
    ],
)
@pytest.mark.usefixtures(
    "feedback_dataset_guidelines",
    "feedback_dataset_fields",
    "feedback_dataset_questions",
    "feedback_dataset_records_with_paired_suggestions",
)
def test_responses_per_user(
    feedback_dataset_guidelines: str,
    feedback_dataset_fields: List["AllowedFieldTypes"],
    feedback_dataset_questions: List["AllowedQuestionTypes"],
    feedback_dataset_records_with_paired_suggestions: List[FeedbackRecord],
    question: str,
    status: str,
    num_responses: int,
):
    dataset = FeedbackDataset(
        guidelines=feedback_dataset_guidelines,
        fields=feedback_dataset_fields,
        questions=feedback_dataset_questions,
    )
    dataset.add_records(records=feedback_dataset_records_with_paired_suggestions)

    responses_per_user, suggestions = get_responses_per_user(dataset, question, response_status=status)
    if status != "submitted":
        num_users = 0
        assert len(responses_per_user) == num_users  # number of users
    else:
        num_users = 3
        assert len(responses_per_user) == num_users  # number of users
        assert isinstance(responses_per_user, dict)
        responses = responses_per_user[list(responses_per_user.keys())[0]]
        assert len(suggestions) == len(responses)
        assert len(responses) == num_responses