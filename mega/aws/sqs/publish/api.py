from logging import INFO, DEBUG
from typing import Optional

from mega.aws.payload import Payload, serialize_payload
from mega.aws.sqs.api import BaseSqsApi


class SqsPublisher(BaseSqsApi):

    def send_payload(self, payload: Payload, queue_url: Optional[str] = None, binary_encoding=False) -> str:
        serialized = serialize_payload(payload, binary_encoding=binary_encoding)
        return self.send_raw_message(serialized, queue_url=queue_url)

    def send_raw_message(self, body: str, queue_url: Optional[str] = None) -> str:
        queue_url = self._get_queue_url(queue_url)

        response = self._client.send_message(
            QueueUrl=queue_url,
            MessageBody=body,
        )

        message_id = response.get('MessageId')
        self._log(INFO, queue_url, message_id, 'Sent SQS message')
        self._log(DEBUG, queue_url, message_id, body)
        return message_id

    def _get_queue_url(self, override_queue_url: Optional[str]) -> str:
        queue_url = override_queue_url or self.queue_url

        if not queue_url:
            raise ValueError('Missing Queue URL')

        return queue_url
