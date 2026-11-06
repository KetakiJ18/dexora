LETTERS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")


class LearningEngine:

    def __init__(self):
        self.reset()

    def reset(self):
        self.current_index = 0
        self.completed = False

    @property
    def letters(self):
        return LETTERS

    @property
    def current_letter(self):
        if self.completed:
            return None

        return LETTERS[self.current_index]

    @property
    def progress(self):
        return self.current_index + 1

    @property
    def total_letters(self):
        return len(LETTERS)

    def advance(self):

        if self.completed:
            return

        self.current_index += 1

        if self.current_index >= self.total_letters:
            self.completed = True

    def reset(self):
        self.current_index = 0
        self.completed = False

    def is_complete(self):
        return self.completed