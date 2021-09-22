from cdev.management.base import BaseCommand


class put_object(BaseCommand):

    def command(self, *args, **kwargs):
        self.stdout.write("Hello")
