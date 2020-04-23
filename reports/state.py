class ReportState(object):
    _state = {}
    
    @property
    def state(self):
        return self._state


    def set_state(self, data):
        print(self._state)
        self._state.update(data)


report_state = ReportState()
