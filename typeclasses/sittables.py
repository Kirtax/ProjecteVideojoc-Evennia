from typeclasses.objects import Object
from commands.sittables import CmdSetSit

class Sittable(Object):

    def at_object_creation(self):
        self.cmdset.add_default(CmdSetSit)

    def do_sit(self, sitter):
        """
        Called when trying to sit on/in this object.

        Args:
            sitter (Object): The one trying to sit down.

        """

        current = self.db.sitter
        if current:
            if current == sitter:
                sitter.msg(f"You are already sitting on {self.key}.")
            else:
                sitter.msg(f"You can't sit on {self.key} "
                        f"- {current.key} is already sitting there!")
            return
        self.db.sitter = sitter
        sitter.db.is_sitting = self
        sitter.msg(f"You sit on {self.key}")


    def do_stand(self, stander):
        """
        Called when trying to stand from this object.

        Args:
            stander (Object): The one trying to stand up.

        """
        current = self.db.sitter
        if not stander == current:
            stander.msg(f"You are not sitting on {self.key}.")
        else:
            self.db.sitter = None
            del stander.db.is_sitting
            stander.msg(f"You stand up from {self.key}.")