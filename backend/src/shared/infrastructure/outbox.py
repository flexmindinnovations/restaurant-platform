"""Transactional outbox pattern for reliable event publishing.

Events are first written to an outbox table within the same database transaction,
then a background worker publishes them to the event bus and marks them as processed.
"""
