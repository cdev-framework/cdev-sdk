from core.constructs.settings import Settings


class SlackBotSettings(Settings):
    SLACK_SECRET: str = ""
    SLACK_BOT_OAUTH_TOKEN: str = ""
