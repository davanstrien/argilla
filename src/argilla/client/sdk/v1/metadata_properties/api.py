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

from typing import Union
from uuid import UUID

import httpx

from argilla.client.sdk.commons.errors_handler import handle_response_error
from argilla.client.sdk.commons.models import ErrorMessage, HTTPValidationError, Response
from argilla.client.sdk.v1.metadata_properties.models import FeedbackMetadataPropertyModel


def delete_metadata_property(
    client: httpx.Client, id: UUID
) -> Response[Union[FeedbackMetadataPropertyModel, ErrorMessage, HTTPValidationError]]:
    """Sends a DELETE request to `/api/v1/metadata_properties/{id}` endpoint to delete a
    metadata property from a `FeedbackTask` dataset in Argilla.

    Args:
        client: the authenticated Argilla client to be used to send the request to the API.
        id: the id of the metadata property to be deleted in Argilla.

    Returns:
        A `Response` object containing a `parsed` attribute with the parsed response if
        the request was successful, which is a `FeedbackMetadataPropertyModel`.
    """
    url = f"/api/v1/metadata-properties/{id}"

    response = client.delete(url=url)

    if response.status_code == 200:
        response_obj = Response.from_httpx_response(response)
        response_obj.parsed = FeedbackMetadataPropertyModel.parse_raw(response.content)
        return response_obj
    return handle_response_error(response)