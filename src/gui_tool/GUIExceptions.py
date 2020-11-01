from ..signals import StopSignal

class ManualTaggingAbortedException(StopSignal):
    '''Raise when user aborts the tagging'''

class ManualTaggingExitedException(StopSignal):
    '''Raise when user aborts the tagging'''
