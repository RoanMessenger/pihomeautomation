def controller(state, settings, inputs):
    
    newState        = dict(state)
    outputs         = {}
    settingsChanges = {}
    messages        = []
    return (newState, outputs, settingsChanges, messages)
