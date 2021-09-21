from cdev.management.base import BaseCommand


class put_object(BaseCommand):

    def command(self, *args, **kwargs):
        print(f"Put Object args -> {args}")
        print(f"Put Object kwargs -> {kwargs}")
