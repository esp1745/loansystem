# loanApp/context_processors.py
def custom_processor(request):
    return {
        'some_variable': 'value',
    }
