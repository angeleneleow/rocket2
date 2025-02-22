"""Feature random public channels."""
from slack import WebClient
from interface.slack import Bot
from random import choice
from .base import ModuleBase
from typing import Dict, Any
from flask import Flask
from config import Config
import logging


class RandomChannelPromoter(ModuleBase):
    """Module that promotes a random channel every Saturday."""

    NAME = 'Feature random channels'

    def __init__(self,
                 flask_app: Flask,
                 config: Config):
        """Initialize the object."""
        self.default_channel = config.slack_announcement_channel
        self.bot = Bot(WebClient(config.slack_api_token),
                       config.slack_notification_channel)

    def get_job_args(self) -> Dict[str, Any]:
        """Get job configuration arguments for apscheduler."""
        return {'trigger':      'cron',
                'day_of_week':  'sat',
                'hour':         12,
                'name':         self.NAME}

    def do_it(self):
        """Select and post random channels to #general."""
        channels = self.bot.get_channels()

        # Find an appropriate random channel
        rand_channel = choice(channels)
        checked = 0
        while rand_channel['is_archived'] or rand_channel['is_private']:
            rand_channel = choice(channels)
            checked += 1
            if checked > len(channels):
                logging.error('No non-archived or non-private channels found')
                return

        channel_id, channel_name = rand_channel['id'], rand_channel['name']
        self.bot.send_to_channel(f'Featured channel of the week: ' +
                                 f'<#{channel_id}|{channel_name}>!',
                                 self.default_channel)

        logging.info(f'Featured #{channel_name}')
