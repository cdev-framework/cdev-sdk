from cdev.management.base import BaseCommand


class put_object(BaseCommand):

    def command(self, *args, **kwargs):
        print(f"Put Item args -> {args}")
        print(f"Put Item kwargs -> {kwargs}")
