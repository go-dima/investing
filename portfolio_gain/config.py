class Config(object):
    def __init__(self, **kwargs):
        for arg in kwargs:
            setattr(self, arg, kwargs[arg])

    def __str__(self):
        '''
        String-representation as newline-separated string useful in print()
        '''
        state = [f'{attr}: {val}' for (attr, val) in self.__dict__.items()]
        return '\n'.join(state)
